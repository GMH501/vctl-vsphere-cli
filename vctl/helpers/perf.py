from datetime import datetime, timedelta
from pyVmomi import vim


def get_perfs(content):
    perf_dict = {}
    perfList = content.perfManager.perfCounter
    for counter in perfList:
        counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
        perf_dict[counter_full] = counter.key
    return perf_dict


def get_perfs_id(content):
    perf_dict = {}
    perfList = content.perfManager.perfCounter
    for counter in perfList:
        counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
        perf_dict[counter.key] = counter_full
    return perf_dict


def get_perfs_unit(content):
    perf_dict = {}
    perfList = content.perfManager.perfCounter
    for counter in perfList:
        perf_dict[counter.key] = counter.unitInfo.key
    return perf_dict


def print_perfs(content):
    perf_dict = {}
    perfList = content.perfManager.perfCounter
    for counter in perfList:
        counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
        counter_info = "{:<5}  {:<49}  {:<19}  {:<11}  {}".format(
                                        counter.key,
                                        counter_full, 
                                        counter.unitInfo.key,
                                        counter.rollupType ,
                                        counter.nameInfo.label)
        print(counter_info)


def perf_id(content, counter_name):
    counter_value = None
    perf_dict = get_perfs(content)
    counter_value = perf_dict[counter_name]
    return counter_value

def getPerfById(content):
    counter_value = None
    perf_dict = get_perfs(content)
    counter_value = perf_dict[counter_name]
    return counter_value


def BuildQuery(content, counter_names, machine, instance='', time_measure='minutes', unit=1, interval=20, sample=1):
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
        metricIds = [vim.PerformanceManager.MetricId(counterId=perf_id(content, counter_name)) for counter_name in counter_names]
        query = vim.PerformanceManager.QuerySpec(#intervalId=interval,
                                                 entity=machine,
                                                 metricId=metricIds,
                                                 startTime=startTime,
                                                 #maxSample=sample,
                                                 endTime=endTime)
        perfResults = perfManager.QueryPerf(querySpec=[query])
        if perfResults:
            return perfResults
    except Exception as e:
        raise e


class Perf:
    def __init__(self, content, results):
        self.results= results
        self.perfsId = get_perfs_id(content)
        self.perfsUnit = get_perfs_unit(content)
        self.name = results[0].entity.name
        self.timestamps = [sample.timestamp for sample in results[0].sampleInfo]
        self.num_timestamps = len(self.timestamps)
        self.values = [
            {"counterId": result.id.counterId, 
             "counterName": self.perfsId[result.id.counterId], 
             "counterUnit": self.perfsUnit[result.id.counterId],
             "values" : _format(result.value, self.perfsUnit[result.id.counterId], self.num_timestamps)
            } for result in results[0].value
        ]
        self.num_metrics = len(results[0].value)


def _format(values:list, counterUnit:int, num_timestamps:int) -> list: 
    formatted_list = []
    if values == []:
        formatted_list = ["null" for i in range(0, num_timestamps)]
        return formatted_list
    if counterUnit == 'percent':
        formatted_list = [value / 100 for value in values]
        return formatted_list
    return values


def get_vms(content):
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        [vim.VirtualMachine],
                                                        True)
    vms = list(container.view)
    container.Destroy()
    return vms
