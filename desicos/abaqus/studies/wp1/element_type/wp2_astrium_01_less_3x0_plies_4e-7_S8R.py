#
study_name_prefix = 'wp2_astrium_01_less_3x0_plies_4e-7_S8R'
#
import numpy as np
#
meshes =  {\
          'NUMEL_080':  80.,
          'NUMEL_120': 120.,
          'NUMEL_160': 160.,
          'NUMEL_180': 180.,
          #'NUMEL_320': 320.,
          #'NUMEL_360': 360.,
         }
studies = {}
for meshname, numel_r in meshes.iteritems():
    study_name = study_name_prefix + '_' + meshname
    source_python = r'\\MA-CASTRO\abaqus-conecyl-python'
    import sys
    import os
    study_dir  = os.path.join( r'C:\Temp','abaqus',study_name )
    if not os.path.isdir( study_dir ):
        os.makedirs( study_dir )
    python_dir = os.path.join( study_dir, 'abaqus-conecyl-python' )
    output_dir = os.path.join( study_dir,'outputs' )
    print 'configuring folders...'
    print '\t' + python_dir
    print '\t' + output_dir
    if not os.path.isdir( output_dir ):
        os.makedirs( output_dir )
    if os.path.isdir( python_dir ):
        os.system('rmdir /s /q ' + python_dir)
    os.makedirs( python_dir )
    os.system('xcopy /s ' + source_python + ' ' + python_dir + '')
    sys.path.append( python_dir )
    #
    import study
    study = reload( study )
    from study import Study
    std = Study()
    std.name = study_name
    std.rebuild()
    #ploads = [ 0.,0.2,0.5,0.7,1.,2.,3.,4.,5.,10. ]
    ploads = [ 10. ]
    pt = 0.5
    cname = 'astrium_1_less_3x0_plies'
    for pload in ploads:
        cc = std.add_cc_fromDB( cname )
        cc.elem_type = 'S8R'
        #cc.request_stress_output = True
        cc.separate_load_steps = True
        cc.artificial_damping = True
        cc.damping_factor = 4.e-7
        cc.adaptiveDampingRatio = False
        cc.output_requests = ('U', 'NFORC')
        cc.numel_r = numel_r
        cc.numel_hr_ratio = None
        cc.meshname = meshname
        cc.impconf.ploads = []
        cc.impconf.add_pload(
            theta=  0.,
            pt = pt,
            pltotal = pload )
        cc.axial_displ = 1.0
        cc.rebuild()
    std.create_models(read_outputs=True)
    studies[ std.name ] = std
