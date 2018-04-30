# -*- mode: python; coding: utf-8 -*-

# Copyright © 2018 by Jeffrey C. Ollie
#
# This file is part of Mediacom Internet Usage Exporter.
#
# Mediacom Internet Usage Exporter is free software: you can
# redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Mediacom Internet Usage Exporter is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import arrow
import os
import re
import requests
import time

from prometheus_client import start_http_server
from prometheus_client import Gauge

package_re = re.compile(r'<span class="titleBlack">(.*?)</span><br>\n(\d+)(G|M)bps Download / (\d+)(G|M)bps Upload<br>\n(\d+) (G|M)B monthly usage allowance')
usage_period_re = re.compile(r'usageCurrentCategories\.push\(\'(.{3} \d{1,2}, \d{4}) - (.{3} \d{1,2}, \d{4})\'\);')
usage_total_re = re.compile(r'usageCurrentData\.push\((\d+(?:\.\d+)?)\);')
usage_upload_re = re.compile(r'usageCurrentUpData\.push\((\d+(?:\.\d+)?)\);')
usage_download_re = re.compile(r'usageCurrentDnData\.push\((\d+(?:\.\d+)?)\);')
usage_remaining_days_re = re.compile(r'with (\d+) days? remaining this month')
usage_re = re.compile(r'(\d+(?:\.\d+)?) GB of (\d+(?:\.\d+)?) GB used')
usage_measurement_timestamp_re = re.compile(r'Data usage above as measured by Mediacom as of (\d+/\d+/\d+ \d+:\d+)')

customer_id = os.environ['CUSTOMER_ID']

package_download_speed = Gauge('mediacom_internet_package_download_speed', 'Mediacom Package Download Speed', ['customer_id', 'package_name'])
package_upload_speed = Gauge('mediacom_internet_package_upload_speed', 'Mediacom Package Upload Speed', ['customer_id', 'package_name'])
package_allowance_bytes = Gauge('mediacom_internet_package_allowance_bytes', 'Mediacom Package Allowance', ['customer_id', 'package_name'])
usage_total_bytes = Gauge('mediacom_internet_usage_total_bytes', 'Current Total Usage', ['customer_id']).labels(customer_id)
usage_download_bytes = Gauge('mediacom_internet_usage_download_bytes', 'Current Download Usage', ['customer_id']).labels(customer_id)
usage_upload_bytes = Gauge('mediacom_internet_usage_upload_bytes', 'Current Upload Usage', ['customer_id']).labels(customer_id)
usage_allowance_bytes = Gauge('mediacom_internet_usage_allowance_bytes', 'Allowance', ['customer_id']).labels(customer_id)
usage_remaining_days = Gauge('mediacom_internet_usage_remaining_days', 'Remaining Days', ['customer_id']).labels(customer_id)
usage_measurement_timestamp = Gauge('mediacom_internet_usage_measurement_timestamp', 'Measurement Timestamp', ['customer_id']).labels(customer_id)
usage_period_start = Gauge('mediacom_internet_usage_period_start_timestamp', 'Period Start', ['customer_id']).labels(customer_id)
usage_period_end = Gauge('mediacom_internet_usage_period_end_timestamp', 'Period End', ['customer_id']).labels(customer_id)

if 'REPORT_URL' in os.environ:
    report_url = os.environ['REPORT_URL']
else:
    report_url = 'http://50.19.209.155/um/usage.action'

if 'REPORT_TIMEZONE' in os.environ:
    report_timezone = os.environ['REPORT_TIMEZONE']
else:
    report_timezone = 'America/Chicago'

start_http_server(9336)

while True:
    result = requests.post(report_url, data = { 'custId': customer_id })

    match = package_re.search(result.text)
    if match:
        package_name = match.group(1)

        download_speed = int(match.group(2))
        if match.group(3) == 'M':
            download_speed *= pow(2,20)
        elif match.group(3) == 'G':
            download_speed *= pow(2,30)

        package_download_speed.labels(customer_id, package_name).set(download_speed)

        upload_speed = int(match.group(4))
        if match.group(5) == 'M':
            upload_speed *= pow(2,20)
        elif match.group(5) == 'G':
            upload_speed *= pow(2,30)

        package_upload_speed.labels(customer_id, package_name).set(upload_speed)

        allowance_bytes = int(match.group(6))
        if match.group(7) == 'M':
            allowance_bytes *= pow(2,20)
        elif match.group(7) == 'G':
            allowance_bytes *= pow(2,30)

        package_allowance_bytes.labels(customer_id, match.group(1)).set(allowance_bytes)

    match = usage_period_re.search(result.text)
    if match:
        ts = arrow.get(match.group(1), 'MMM D, YYYY').replace(hour = 0, minute = 0, second = 0, tzinfo = report_timezone)
        usage_period_start.set(ts.float_timestamp)

        ts = arrow.get(match.group(2), 'MMM D, YYYY').replace(hour = 0, minute = 0, second = 0, tzinfo = report_timezone).shift(days = 1)
        usage_period_end.set(ts.float_timestamp)

    match = usage_total_re.search(result.text)
    if match:
        usage_total_bytes.set(float(match.group(1)) * pow(2,30))

    match = usage_download_re.search(result.text)
    if match:
        usage_download_bytes.set(float(match.group(1)) * pow(2,30))

    match = usage_upload_re.search(result.text)
    if match:
        usage_upload_bytes.set(float(match.group(1)) * pow(2,30))

    match = usage_remaining_days_re.search(result.text)
    if match:
        usage_remaining_days.set(int(match.group(1)))

    match = usage_re.search(result.text)
    if match:
        usage_allowance_bytes.set(float(match.group(2)) * pow(2,30))

    match = usage_measurement_timestamp_re.search(result.text)
    if match:
        ts = arrow.get(match.group(1), 'M/D/YYYY H:mm').replace(tzinfo=report_timezone)
        usage_measurement_timestamp.set(ts.float_timestamp)

    time.sleep(60)
