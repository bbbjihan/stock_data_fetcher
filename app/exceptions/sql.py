from dataclasses import dataclass
from fastapi import HTTPException, status

from typing import Optional, Dict, Any, ClassVar, Mapping
from starlette.requests import Request

'''
 File "C:\Users\korea\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.9_qbz5n2kfra8p0\LocalCache\local-packages\Python39\site-packages\pymysql\err.py", line 143, in raise_mysql_exception
    raise errorclass(errno, errval)
sqlalchemy.exc.ProgrammingError: (pymysql.err.ProgrammingError) (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'as SearchName ON RD7.ISU_CODE = SearchName.ISU_CODE' at line 23")

'''