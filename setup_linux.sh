DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
x='PYTHONPATH=$PYHTONPATH:'+$DIR
echo $x >> ~/.profile
source ~/.profile
