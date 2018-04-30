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

FROM python:3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir arrow prometheus_client requests

COPY mediacom-internet-usage-exporter.py .

EXPOSE 9336

CMD ["python", "./mediacom-internet-usage-exporter.py"]
