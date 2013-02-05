#!/bin/sh
# Author : Rajat Khanduja
# Script to download captchas from the webmail page

i=0

while [ $i -ne 100 ]
do
  wget --no-proxy --no-check-certificate \
  https://webmail.iitg.ernet.in/plugins/captcha/backends/watercap/image_generator.php -O $i.png
  i=$((i + 1))
done
