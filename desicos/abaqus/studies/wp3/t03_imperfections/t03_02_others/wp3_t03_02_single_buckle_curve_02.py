#
cname = 'huehne_2008_z07'
meshes = {\
           'NUMEL_120' : 120.,
         }
#
pload  = 0.
studies = []
for meshname, numel_r in meshes.iteritems():
    study_name = 'wp3_t03_02_single_buckle_curve_02'
    ###########################################
    ########  FILE MANAGEMENT SECTION  ########
    ###########################################
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
    if not os.path.isdir( python_dir ):
        os.makedirs( python_dir )
    os.system('xcopy /s /y ' + source_python + ' ' + python_dir + '')
    sys.path.append( python_dir )
    ###########################################
    import study
    study = reload( study )
    std = study.Study()
    std.name = study_name
    std.rebuild()
    dimples = {\
                1:[ 45, 500, 0.04],
                2:[ 45, 500, 0.08],
                3:[ 45, 500, 0.24],
                4:[ 45, 500, 0.40],
                5:[ 45, 500, 0.64],
                6:[ 45, 500, 0.72],
                7:[ 45, 500, 0.80],
                8:[ 45, 500, 1.32],
                9:[ 45, 500, 2.00],
               10:[ 45, 500, 2.64],
              }
    for key, dimple in dimples.iteritems():
        cc = std.add_cc_fromDB( cname )
        cc.meshname = meshname
        cc.damping_factor2 = 1.e-7
        cc.initialInc2 = 1.e-3
        cc.minInc2 = 1.e-6
        cc.maxInc2 = 1.e-3
        cc.maxNumInc2 = 100000
        cc.impconf.ploads = []
        cc.impconf.add_dimple( 0., 0.5,\
                                      dimple[0], dimple[1], dimple[2] )
        cc.numel_r    = numel_r
        cc.elem_type  = 'S8R5'
        cc.axial_displ= 0.46
        cc.impconf.rename = False
        cc.impconf.name = 'SB_%03d' % int(round(dimple[2]*100))
        cc.create_model()
        cc.write_job()
    std.create_run_file()
