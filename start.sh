# stop script on error
set -e

# Check to see if root CA file exists, download if not
if [ ! -f ./root-CA.crt ]; then
  printf "\nDownloading AWS IoT Root CA certificate from AWS...\n"
  curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > root-CA.crt
fi

# install AWS Device SDK for Python if not already installed
if [ ! -d ./aws-iot-device-sdk-python ]; then
  printf "\nInstalling AWS SDK...\n"
  git clone https://github.com/aws/aws-iot-device-sdk-python.git
  pushd aws-iot-device-sdk-python
  python3 setup.py install
  popd
fi

# run pub/sub sample app using certificates downloaded in package
printf "\nStarting send of IoT data...\n"
python3 -m send_to_iot.py -e a3aptjr7g78e5m-ats.iot.ap-southeast-2.amazonaws.com -r ./creds/root-CA.crt -c ./creds/hsk_sensor_1.cert.pem -k ./creds/hsk_sensor_1.private.key -t hsktopic