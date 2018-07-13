# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 11:11:05 2018

@author: Ulrik Åkesson
"""

from fuzzyPID import fuzzyPID as fPID

Kp, Kd = fPID(-80, -40)
print(Kp, Kd)