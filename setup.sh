
#export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/usr/include/python2.7/"
export LC_ALL=''
export RCM_NO_COLOR=0
export RCM_GRID_ENV=0
export LZT_PATH=`pwd`


cd build
rm -rf lib
mkdir lib
for file in "`pwd`"/*/*/*.pcm
do
  echo "ln -sf $file lib"
  ln -sf $file lib
done 



if [[ "$OSTYPE" == "darwin"* ]]; then
  for file in "`pwd`"/*.dylib
  do
    echo "ln -sf $file lib"
    ln -sf $file lib
  done 

else
  for file in "`pwd`"/*.so
  do
    echo "ln -sf $file lib"
    ln -sf $file lib
  done 
fi



export LD_LIBRARY_PATH=`pwd`/lib:$LD_LIBRARY_PATH
export PATH=`pwd`/lib:$PATH
export PYTHONPATH=`pwd`/python:$PYTHONPATH
cd ..
export PATH=$PATH:$PWD/scripts
export PATH=$PATH:$PWD/generator/PythiaGenerator/share




