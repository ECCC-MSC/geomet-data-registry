# =================================================================
#
# Author: Etienne Pelletier <etienne.pelletier@canada.ca>
# Author: Tom Kralidis <tom.kralidis@canada.ca>
#
# Copyright (c) 2020 Etienne Pelletier
# Copyright (c) 2020 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

# IMPORTANT: When using a Unix command in a new cron job, use the full path to the command (e.g. /bin/bash, /bin/cp, etc.).

##############################################################################
# data cleanups

### REPS/GEPS: every day at 00:35, clean out content older than 3 days
# We never delete CanSIPS data because serving all archives is in scope for GeoMet-Weather / CCCS
35 * * * * geoadm /usr/bin/find $GDR_DATADIR/ensemble/ -type f -not -path "$GDR_DATADIR/ensemble/cansips/*" -mtime +3 -exec rm {} \; > /dev/null 2>&1

### GDPS: twice a day at 02:05 and 14:05, clean out content older than 35 hours
05 2,14 * * * geoadm /usr/bin/find $GDR_DATADIR/model_gem_global/ -type f -mmin +2100 -exec rm {} \; > /dev/null 2>&1

### HRDPS: twice a day at 02:05 and 14:05, clean out content older than 35 hours
05 2,14 * * * geoadm /usr/bin/find $GDR_DATADIR/model_hrdps/ -type f -mmin +2100 -exec rm {} \; > /dev/null 2>&1

### RDPS/CGSL: twice a day at 2:05 and 14:05, clean out content older than 30 hours
05 2,14 * * * geoadm /usr/bin/find $GDR_DATADIR/model_gem_regional/ -type f -mmin +1800 -exec rm {} \; > /dev/null 2>&1

### GIOPS: twice a day at 4:35 and 16:35, clean out netcdf content older than 4 days
35 4,16 * * * geoadm /usr/bin/find $GDR_DATADIR/model_giops/netcdf/ -type f -mtime +4 -exec rm {} \; > /dev/null 2>&1

### WCPS: twice a day at 4:35 and 16:35, clean out netcdf content older than 7 days
35 4,16 * * * geoadm /usr/bin/find $GDR_DATADIR/model_wcps/nemo/netcdf/ -type f -mtime +7 -exec rm {} \; > /dev/null 2>&1

### GDWPS/RDWPS: twice a day a 4:25 and 16:25 clean out model_wave files older than 35 hours
25 4,16 * * * geoadm /usr/bin/find $GDR_DATADIR/model_wave/ -type f -mmin +2100 -exec rm {} \; > /dev/null 2>&1

# every day at 0300h, clean out empty MetPX directories
0 3 * * * geoadm /usr/bin/find $GDR_DATADIR -type d -empty -delete > /dev/null 2>&1

##############################################################################
