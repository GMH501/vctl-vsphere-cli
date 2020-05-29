from datetime import datetime, timedelta
from pyVmomi import vim


def get_perfs(content):
    perf_dict = {}
    try:
        perfList = content.perfManager.perfCounter
        for counter in perfList:
            counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
            perf_dict[counter_full] = counter.key
        return perf_dict
    except:
        raise


def perf_id(content, counter_name):
    counter_value = None
    try:
        perf_dict = get_perfs(content)
        counter_value = perf_dict[counter_name]
        return counter_value
    except:
        raise


def BuildQuery(content, counter_name, instance, machine, time_measure, unit, interval):
    """
    se instance = "" prendiamo l'usage dell'host, mentre se vogliamo ad esempio la vcpu n°8 dell'host dobbiamo fare instance = "8"
    l'intervalId deve stare a 20 secondi
    """
    if time_measure == 'hours':
        startTime = datetime.now() - timedelta(hours=unit)
    elif time_measure == 'minutes':
        startTime = datetime.now() - timedelta(minutes=unit)
    elif time_measure == 'weeks':
        startTime = datetime.now() - timedelta(weeks=unit)
    elif time_measure != 'hours' or time_measure != 'minutes' or time_measure != 'weeks':
        raise Exception('Use "hours", "minutes", or "weeks" as a unit of time measurement.')
    endTime = datetime.now()
    try:
        perfManager = content.perfManager
        counterId = perf_id(content, counter_name)
        metricId = vim.PerformanceManager.MetricId(counterId=counterId, instance=instance)
        query = vim.PerformanceManager.QuerySpec(intervalId=interval,
                                                 entity=machine,
                                                 metricId=[metricId],
                                                 startTime=startTime,
                                                 endTime=endTime)
        perfResults = perfManager.QueryPerf(querySpec=[query])
        if perfResults:
            return perfResults
    except Exception as e:
        raise e
