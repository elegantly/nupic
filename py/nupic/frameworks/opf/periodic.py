# ----------------------------------------------------------------------
#  Copyright (C) 2011 Numenta Inc. All rights reserved.
#
#  The information and source code contained herein is the
#  exclusive property of Numenta Inc. No part of this software
#  may be used, reproduced, stored or distributed in any form,
#  without explicit written authorization from Numenta Inc.
# ----------------------------------------------------------------------

from collections import namedtuple

########################################################################
# Passed as parameter to ActivityMgr
#
# repeating: True if the activity is a repeating activite, False if one-shot
# period: period of activity's execution (number of "ticks")
# cb: a callable to call upon expiration of period; will be called
#     as cb()
PeriodicActivityRequest = namedtuple("PeriodicActivityRequest",
                                     ("repeating", "period", "cb"))

########################################################################
class PeriodicActivityMgr(object):
  """
  TODO: move to shared script so that we can share it with OpfRunExperiment
  """

  # iteratorHolder: a list holding one iterator; we use a list so that we can
  #           replace the iterator for repeating activities (a tuple would not
  #           allow it if the field was an imutable value)
  Activity = namedtuple("Activity", ("repeating",
                                     "period",
                                     "cb",
                                     "iteratorHolder"))

  def __init__(self, requestedActivities=[]):
    """
    requestedActivities: a sequence of PeriodicActivityRequest elements
    """

    self.__activities = []
    self.__appendActivities(requestedActivities)

    return


  def addActivities(self, periodicActivities):
    """ Adds activities

    periodicActivities: A sequence of PeriodicActivityRequest elements
    """

    self.__appendActivities(periodicActivities)

    return


  def tick(self):
    """ Activity tick handler; services all activities

    Returns:      True if controlling iterator says it's okay to keep going;
                  False to stop
    """

    # Run activities whose time has come
    for act in self.__activities:
      if not act.iteratorHolder[0]:
        continue

      try:
        next(act.iteratorHolder[0])
      except StopIteration:
        act.cb()
        if act.repeating:
          act.iteratorHolder[0] = iter(xrange(act.period-1))
        else:
          act.iteratorHolder[0] = None

    return True


  def __appendActivities(self, periodicActivities):
    """
    periodicActivities: A sequence of PeriodicActivityRequest elements
    """

    for req in periodicActivities:
      act =   self.Activity(repeating=req.repeating,
                            period=req.period,
                            cb=req.cb,
                            iteratorHolder=[iter(xrange(req.period-1))])
      self.__activities.append(act)

    return