#!/usr/bin/env python
import sys,os, time
import numpy as np
import subprocess
import pickle
import model_ELM
from concurrent.futures import ProcessPoolExecutor, as_completed
from optparse import OptionParser

#Python code used to manage the ensemble simulations 
#  and perform post-processing of model output.

mycase = None
processes = []
_WORKER_CASE = None

#get the node file and parse
def get_nodelist():
  mynodes=[]
  nodelist=os.environ['SLURM_JOB_NODELIST'].split('xxx')
  print(nodelist)
  for n in nodelist:
    if ('[' in n):
        node_prefix=n.split('[')[0]
        nodelist2=n.split('[')[1].split(',')
        for n2 in nodelist2:
          if ('-' in n2):
            firstnode=n2.split('-')[0]
            lastnode=n2.split('-')[1].strip(']')
            for nn in range(int(firstnode),int(lastnode)+1):
              if ('baseline' in mycase.machine):
                nstr = str(nn)
              else:
                nstr = str(10000+nn)[1:]
              mynodes.append(node_prefix+nstr)
          else:
              if ('baseline' in mycase.machine):
                nstr=str(n2).strip(']')
              else:
                nstr=str(10000+n2)[1:].strip(']')
              mynodes.append(node_prefix+nstr)
    else:
        mynodes.append(n)
  return mynodes

def get_node_submit(pactive,process_nodes,mynodes):
    node_submit=0
    for n in range(0,len(mynodes)):
         ctn=0    #Counter for active processes on each node
         for p in range(0,len(processes)):
                if pactive[p] == 1 and process_nodes[p] == n:
                    ctn=ctn+1
         if (ctn < mycase.npernode/mycase.np):
             #If this node is not full, submit
             node_submit=n
    return(node_submit)

def check_run_success(n, case=None):
    if case is None:
        case = mycase
    success=False
    jobst = str(100000+n)
    rundir = case.runroot+'/UQ/'+case.casename+'/g'+jobst[1:]
    yst = str(10000+case.startyear+case.run_n)[1:]
    #yst = '2010'
    if (os.path.isfile(rundir+'/'+case.casename+'.elm.r.'+yst+'-01-01-00000.nc')):
        success=True
    return success

def active_processes(processes,process_jobnum,process_hang):
    """Returns the number of processes that are still running."""
    pactive=[]
    n=0
    for process in processes:
        if process.poll() is None:  # None means the process is still running
            #Check if final restart file created
            pactive.append(1)
            if (check_run_success(process_jobnum[n])):
                process_hang[n] = process_hang[n]+1
            if (process_hang[n] > 30):
                process.kill()  # Force kill the process
        else:
            pactive.append(0)
        n=n+1
    return pactive

def postprocess_one_member(ens_num):
    """Worker: postprocess one ensemble member and return arrays for the parent."""
    case = _WORKER_CASE
    member_out = {}
    taxis = None
    if (case.postproc_vars != []):
        for v in case.postproc_vars:
          hnum=1
          mypfts=[0]
          if ('_pft' in v):
              hnum=2
              mypfts=case.postproc_pfts
          for p in mypfts:
            kwargs = dict(ens_num=ens_num, startyear=case.postproc_startyear,
                          endyear=case.postproc_endyear, index=p, hnum=hnum,
                          write_output=False)
            if (case.postproc_freq == 'daily' or case.postproc_freq == 'hourly'):
              values_out, var_out, taxis = case.postprocess(v, **kwargs)
            elif (case.postproc_freq == 'monthly'):
              values_out, var_out, taxis = case.postprocess(v, dailytomonthly=True, **kwargs)
            elif (case.postproc_freq == 'annual'):
              values_out, var_out, taxis = case.postprocess(v, annualmean=True, **kwargs)
            else:
              continue
            member_out[var_out] = np.asarray(values_out, dtype=float)
    return ens_num, member_out, taxis

def _init_postprocess_worker(case):
    global _WORKER_CASE
    _WORKER_CASE = case
    _WORKER_CASE.output = {}

def run_parallel_postprocess(n_workers):
    members = list(range(1, mycase.nsamples+1))
    n_workers = max(1, min(int(n_workers), mycase.nsamples))
    print('All '+str(mycase.nsamples)+' ensemble members succeeded; '
          'postprocessing with '+str(n_workers)+' workers')
    mycase.output = {}
    with ProcessPoolExecutor(max_workers=n_workers,
                             initializer=_init_postprocess_worker,
                             initargs=(mycase,)) as executor:
        futures = [executor.submit(postprocess_one_member, n) for n in members]
        for fut in as_completed(futures):
            ens_num, member_out, taxis = fut.result()
            print('Postprocessed ensemble member '+str(ens_num))
            for var_out, values_out in member_out.items():
                if (not var_out in mycase.output):
                    mycase.output[var_out] = np.zeros([len(values_out), mycase.nsamples], float)
                mycase.output[var_out][:,ens_num-1] = values_out
            if (taxis is not None):
                mycase.output['taxis'] = taxis

def main():
    global mycase, processes

    parser = OptionParser()
    parser.add_option("--case", dest="case", default="", \
                      help="Case name")
    parser.add_option("--postproc_only", dest="postproc_only", default=False, \
                      action="store_true")
    parser.add_option("--UQ_only", dest="UQ_only", default=False, \
                      action="store_true")
    parser.add_option("--n_postproc_workers", dest="n_postproc_workers", default=4, \
                      type="int", help="Worker processes for postprocess (default 4)")
    (options, args) = parser.parse_args()

    #Load case object
    myfile=open('pklfiles/'+options.case+'.pkl','rb')
    mycase=pickle.load(myfile)

    #mycase.postproc_startyear = 2010
    #mycase.postproc_freq = 'monthly'
    if (not options.UQ_only):
        mycase.output = {}
    else:
        print(mycase.output)
        print(mycase.postproc_freq)
        return

    processes=[]
    process_jobnum=[]
    process_hang=[]    #Keep track of how long process has been hanging
    n_job = 1
    if (mycase.noslurm == False):
      process_nodes = []
      mynodes = get_nodelist()

    #Run the simulations
    pactive=[]
    while (n_job <= mycase.nsamples):
      pactive = active_processes(processes,process_jobnum,process_hang)
      if (sum(pactive) < int(mycase.np_ensemble)):
        jobst = str(100000+n_job)
        rundir = mycase.runroot+'/UQ/'+mycase.casename+'/g'+jobst[1:]+'/'
        log_file_path = f"{rundir}e3sm_log.txt"
        #Copy relevant files
        if not options.postproc_only:
          mycase.ensemble_copy(n_job)
        with open(log_file_path, "w") as log_file:
          if (mycase.noslurm == False):
            node_submit=get_node_submit(pactive,process_nodes,mynodes)
            # command = ['srun -n '+str(mycase.np)+' -c 1 -w '+mynodes[node_submit]+' '+mycase.exeroot+'/e3sm.exe']
            # Tianyi Hu added for parallel
            command = ['srun --exact -n '+str(mycase.np)+' -c 1 -w '+mynodes[node_submit]+' '+mycase.exeroot+'/e3sm.exe']
            print(command)
            process_nodes.append(node_submit)
          else:
            command = [mycase.exeroot+'/e3sm.exe']
          if (options.postproc_only):
              command='ls'
          process = subprocess.Popen(command, shell=True, stderr=subprocess.STDOUT, cwd=rundir, stdout=log_file)
          processes.append(process)
          process_jobnum.append(n_job)
          process_hang.append(0)
        n_job=n_job+1
      else:
        time.sleep(1)

    # Wait until every launched e3sm.exe has exited (or been hang-killed)
    pactive = active_processes(processes,process_jobnum,process_hang)
    while (sum(pactive) > 0):
      time.sleep(1)
      pactive = active_processes(processes,process_jobnum,process_hang)

    failed=[]
    for n in range(1, mycase.nsamples+1):
      if (not check_run_success(n)):
        failed.append(n)
        print('Ensemble member '+str(n)+' Failed to complete')
    if (failed):
      print('Skipping postprocess because '+str(len(failed))+' of '+
            str(mycase.nsamples)+' members did not produce the final restart:')
      print(failed)
      sys.exit(1)

    run_parallel_postprocess(options.n_postproc_workers)
    mycase.create_pkl(outdir=mycase.OLMTdir+'/pklfiles/')

#UQ part of code

# if (mycase.postproc_vars != []):
#     #Train surrogate models
#     mycase.train_surrogate(mycase.postproc_vars)
#     
#     #Save postprocessed output
#     mycase.create_pkl(outdir=mycase.OLMTdir+'/pklfiles/')
#     
#     #run GSA
#     mycase.GSA(mycase.postproc_vars)
#     mycase.plot_GSA(mycase.postproc_vars)
#
#     #Save postprocessed output
#     mycase.create_pkl(outdir=mycase.OLMTdir+'/pklfiles/')
#
#     #run MCMC
#     #Set intial values for parameters
#     if (mycase.obs):
#         #parms=((np.array(mycase.ensemble_pmax)+np.array(mycase.ensemble_pmin))/2)
#         #Run MCMC for the observation variables
#         obs_mcmc = [v for v in mycase.postproc_vars if v in mycase.obs.keys()]
#         mycase.MCMC_emcee(obs_mcmc,nwalkers=24,nsteps=10000)
#
#         #Save postprocessed output
#         mycase.create_pkl(outdir=mycase.OLMTdir+'/pklfiles/')

if __name__ == '__main__':
    main()
