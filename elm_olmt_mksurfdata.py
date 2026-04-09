#!/usr/bin/env python
import re, sys
import model_ELM
from OLMTutils import get_machine_info, get_site_info, get_point_list, get_default_diag_vars
import os, glob
import numpy as np
import configparser
import argparse

def load_config(config_file):
    """Load configuration from file and return as dictionary"""
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.optionxform = str  # Preserve case of option names
    config.read(config_file)
    
    # Convert to nested dictionary for easier access
    cfg = {}
    for section in config.sections():
        cfg[section] = {}
        for key, value in config.items(section, raw=False):
            # Strip quotes from the value first
            value = value.strip().strip('\'"')
            # Skip conversion for specific keys
            if key == 'startdate_add_co2':
                cfg[section][key] = str(value)
                continue
            # Handle different data types
            if value.lower() in ['true', 'false']:
                cfg[section][key] = value.lower() == 'true'
            elif not ',' in value:
                # Handle single values
                if value.isdigit():
                    cfg[section][key] = int(value)
                elif value.replace('.', '').replace('-', '').isdigit():
                    cfg[section][key] = float(value)
                else:
                    if 'variables' in key:
                        cfg[section][key] = [value] 
                    else:
                        if value:
                            cfg[section][key] = value 
                        else:
                            cfg[section][key] = ''
            else:
                # Handle comma-separated lists
                items = [x.strip().strip('\'"') for x in value.split(',')]
                # Try to convert to numeric types
                try:
                    # Try int first
                    cfg[section][key] = [int(x) for x in items]
                except ValueError:
                    try:
                        # Try float
                        cfg[section][key] = [float(x) for x in items]
                    except ValueError:
                        if 'variables' in key or 'sites' in key:
                            cfg[section][key] = [str(x) for x in items]
                        else:
                            # Keep as comma-separated string for string lists (except sites)
                            if 'hist_fincl' in key:
                                # Special handling for hist_fincl to keep quotes
                                items = [f"'{x}'" for x in items]
                            cfg[section][key] = ', '.join(items)

    cfg = resolve_placeholders(cfg)
    return cfg

def resolve_placeholders(cfg):
    """Resolve %(variable)s placeholders in the configuration dictionary."""
    placeholder_pattern = re.compile(r"%\(([^)]+)\)s")
    
    for section, options in cfg.items():
        for key, value in options.items():
            if isinstance(value, str):
                # Replace placeholders in the string
                matches = placeholder_pattern.findall(value)
                for match in matches:
                    # Look for the variable in all sections
                    replacement = None
                    for sec, opts in cfg.items():
                        if match in opts:
                            replacement = opts[match]
                            break
                    if replacement is not None:
                        value = value.replace(f"%({match})s", str(replacement))
                cfg[section][key] = value
    return cfg

def main():
    parser = argparse.ArgumentParser(description='Run ELM BGC simulations')
    parser.add_argument('--config', '-c', default='run_config.cfg',
                       help='Configuration file (default: run_config.cfg)')
    args = parser.parse_args()

    print('\n')
    print(f"    *** OLMT ***")
    print(f" This is an experimental code only for creating site surface data")

        # Load configuration
    cfg = load_config(args.config)
    print(f"Loaded configuration from {args.config}")
    
    # Get machine info
    machine_name = cfg['machine'].get('machine_name', '')
    machine, rootdir, inputdata, queue, project, hostname = \
        get_machine_info(machine_name=machine_name)
    print('Machine: '+machine+'\n')
    
    # Override machine defaults with config values if provided
    queue = cfg['machine'].get('queue', queue)
    project = cfg['machine'].get('project', project)
    inputdata = cfg['machine'].get('inputdata', inputdata)
    ptclminfodata = cfg['machine'].get('ptclminfodata')
    caseroot = cfg['machine'].get('caseroot', rootdir + '/e3sm_cases')
    runroot = cfg['machine'].get('runroot', rootdir + '/e3sm_run')
    modelroot = cfg['machine'].get('modelroot', '')
    exeroot = cfg['machine'].get('exeroot', '')
    # exeroot
    print('Run root directory:  '+runroot)
    print('Exe root directory:  '+exeroot)
    print('Case root directory: '+caseroot)
    print('Input data directory: '+inputdata)
    print('PTCLM site data directory: '+ptclminfodata)
    print('Model root directory: '+modelroot+'\n')

    # Site configuration
    runtype = cfg['simulation']['runtype']
    sites = cfg['simulation']['sites']
    if isinstance(sites, str):
        sites = [sites]
    sitegroup = cfg['simulation']['sitegroup']
    numproc = 1
    lat_bounds = [-180,180]
    lon_bounds = [-90, 90]

    use_cpl_bypass = 'False'
    res = cfg['simulation']['res']
    global_pft = cfg['simulation'].get('global_pft', '')
    global_soil = cfg['simulation'].get('glbsoil', '')

    # Crop options
    use_crop = cfg['biogeochemistry'].get('use_crop', False)

    print('Gnerating surface data for site group: '+sitegroup)
    # print('Sites: ',sites)

    # Load case options and treatment options from config file
    case_options = {}
    if 'case_options' in cfg:
        case_options = cfg['case_options'].copy()
    
    # Remove specific file types from temp directory
    temp_dir = 'temp'
    for pattern in ['*.nc', '*.tmp']:
        files_to_remove = glob.glob(os.path.join(temp_dir, pattern))
        for file_path in files_to_remove:
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Warning: Could not remove {file_path}: {e}")
    
    if (sites[0] != ''):
        siteinfo = get_site_info(ptclminfodata, sitegroup=sitegroup)
        for s in sites:
            if not (s in siteinfo.keys()):
                print(s+' not in '+sitegroup+' site group. Exiting.')
                print('Available sites: ',siteinfo.keys())
                sys.exit(1)
        print('Running site(s): ', sites)
        point_list  = []
        region_name = ''

    ensemble=False
    compsets=[1]
    suffix=[1]
    print('\nSurface data info:')

    nsites = len(sites)
    jobnum = np.zeros(len(compsets),int)  #list of submitted job ids

    for site in sites:
        cases={}
        scriptdir=os.getcwd()

        cases = model_ELM.ELMcase(caseid='',compset=['surfacedata'], site=site, \
                                  caseroot=caseroot,runroot=runroot,inputdata=inputdata,modelroot=modelroot, \
                                  machine=machine, exeroot=exeroot, suffix='noneedtoset', queue=queue, project=project,  \
                                  res=res, nyears=0,startyear=0, region_name=region_name, \
                                  lat_bounds=lat_bounds, lon_bounds=lon_bounds, np=numproc, point_list=point_list, \
                                  olmtdir=scriptdir)
        if (site != ''):
            cases.siteinfo = siteinfo[site]
        cases.case_options={}

        # Get the namelist options for this case
        for key in case_options.keys():
            cases.case_options[key] = case_options[key]

        #get the default surface and domain files (to pass to makepointdata)
        #Note:  This requires setting a supported resolution
        cases.surfdata_global = cases.case_options['surffile_global']
        cases.domain_global = cases.case_options['domainfile_global']
        surffile=''
        domainfile=''
        pftdynfile=''
        if ('surffile' in cases.case_options):
            surffile = cases.case_options['surffile']
        elif ('fsurdat' in cases.case_options):
            surffile = cases.case_options['fsurdat']
        if ('domainfile' in cases.case_options):
            domainfile = cases.case_options['domainfile']
        elif ('fatmlndfrc' in cases.case_options):
            domainfile = cases.case_options['fatmlndfrc']
        # if ('pftdynfile' in cases.case_options):
        #     pftdynfile = cases.case_options['pftdynfile']
        # elif ('flanduse_timeseries' in cases.case_options):
        #     pftdynfile = cases.case_options['flanduse_timeseries']

        # surffile  = case_options['fsurdat_out']+\
        #             f'/surfdata_1x1pt_NEON_{site}_{res}_{global_pft}_{global_soil}.nc'
        # domainfile= case_options['fsurdat_out']+f'/domain.lnd.1x1pt_{site}_{res}.nc'
        
        surffile   = os.path.join(case_options['fsurdat_out'], site)
        domainfile = os.path.join(case_options['fdomain_out'], site)
        os.makedirs(surffile, exist_ok=True) 

        surffile  = os.path.join(surffile,f'surfdata_1x1_NEON_{site}_hist_2000_16pfts.nc')
        domainfile= os.path.join(domainfile,f'domain.lnd.1x1pt_{site}.nc')
        
        # if (pftdynfile==''):
        # pftdynfile = cases.runroot+'/surfdata.pftdyn.nc'
        print('Extracting surface data for site: '+site)
        print('Input surfdata file: '+cases.surfdata_global)
        print('Output surfdata file: '+surffile)
        print('Input domain file: '+cases.domain_global)
        print('Output domain file: '+domainfile)

        cases.setup_domain_surfdata(makesurfdat=True,makedomain=True)
        
        os.system('cp -v '+cases.OLMTdir+'/temp/surfdata.nc'+' '+surffile)
        os.system('cp -v '+cases.OLMTdir+'/temp/domain.nc'+' '+domainfile)

    return

if __name__ == "__main__":
    main()