
sudo apt -y install postgresql-server-dev-all
sudo apt -y install libffi-dev
sudo apt -y install libpq-dev

python -m pip install numpy cmake wheel pillow --index-url=http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
pip install torch==2.0.1 -f https://download.pytorch.org/whl/torch_stable.html
python -m pip install --upgrade -r requirements.txt