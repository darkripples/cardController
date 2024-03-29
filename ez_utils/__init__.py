# coding:utf8
"""
easy工具类
"""

from .fls_log import fls_log

from .attrdict import AttrDict as fdic
from .fmt_utils import fmt_null_obj as fnull, e_string as fstr, e_int, e_int_money
from .date_utils import fmt_date as fmt_date, get_day_n as after_date, get_seconds_n as after_seconds, \
    get_interval_day as interval_day, reformat_date_str as reformat_date_str
from .date_utils import FMT_DATETIME, FMT_DATE, FMT_TIME, FMT_DATETIME_SEPARATE
from .file_utils import read_in_chunks as read_file
# from .dbpool import connection, sql_execute
from .err_utils import err_check
from .file_utils import walk_dir, glob_dir
from .read_conf_utils import read_conf

from .help import help
