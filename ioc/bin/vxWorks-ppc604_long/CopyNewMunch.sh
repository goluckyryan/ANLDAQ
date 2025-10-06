## bash script to copy a newly compiled munch file from con6 (the "global_sandbox") to the boot area of dgs1.
cd /dk/fs2/dgs/global_32/ioc/bin/vxWorks-ppc604_long
rm -rf ./gretDet.munch
cp /dk/fs2/dgs/global_sandbox/devel/dgsIoc/bin/vxWorks-ppc604_long/gretDet.munch .

