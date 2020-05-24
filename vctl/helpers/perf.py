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
