#!/usr/bin/env python3
import copy
import logging

from macwinnie_pyhelpers.Metrics import MetricsCollection

metric_names = [
    "example_job_1_result_unit",
    "no_show_example_job_result_unit",
    "example_job_3_result_unit",
]

metric_help = [
    "example job result in “unit” with some representations and an escaped backslash \\",
    "example job result in “unit” with no representations",
    """another example job result in “unit” with representations
with two lines of help information""",
]

metric_type = [
    "counter",
    "histogram",
    None,  # gauge should be default, so just let's assume `None` here
]

metric_values = [
    [
        1,
        5,
        11,
        19,
    ],
    [],
    [
        2.0,
        2.1,
        2.2,
    ],
]

metric_labels = [
    [
        {
            "label1": "label value 1",
            "label2": "label value 2",
            "label3": "label value 3",
            "label4": "label value 4",
        },
        {},
        {
            "label1": "label value 9",
            "label2": "label value 10",
            "label3": "label value 11",
            "label5": "label value 12",
        },
    ],
    [],
    [
        {
            "label1": "label value 1",
            "label2": "label value 2",
            "label3": "label value 3",
            "label4": "label value 4",
        },
        {
            "label1": "label value 5",
            "label2": "label value 6",
            "label3": "label value 7",
            "label4": "label value 8",
        },
        {
            "label1": "label value 9",
            "label2": "label value 10",
            "label3": "label value 11",
            "label4": "label value 12",
        },
    ],
]

metrics_string = """# HELP example_job_1_result_unit example job result in “unit” with some representations and an escaped backslash \\\\
# TYPE example_job_1_result_unit counter
example_job_1_result_unit{label1="label value 1",label2="label value 2",label3="label value 3",label4="label value 4"} 1
example_job_1_result_unit{} 19
example_job_1_result_unit{label1="label value 9",label2="label value 10",label3="label value 11",label5="label value 12"} 11

# HELP example_job_3_result_unit another example job result in “unit” with representations\\nwith two lines of help information
# TYPE example_job_3_result_unit gauge
example_job_3_result_unit{label1="label value 1",label2="label value 2",label3="label value 3",label4="label value 4"} 2.0
example_job_3_result_unit{label1="label value 5",label2="label value 6",label3="label value 7",label4="label value 8"} 2.1
example_job_3_result_unit{label1="label value 9",label2="label value 10",label3="label value 11",label4="label value 12"} 2.2
"""


def prepareMetricsObjectForTest(
    values=None,
    overrideHelp=None,
    overrideNames=None,
    overrideLabels=None,
    overrideTypes=None,
):
    """helper to prepare Metrics objects

    Returns:
        MetricsCollection: the prepared stuff of this test file
    """
    mc = MetricsCollection()
    if values == None:
        values = metric_values
    if overrideHelp == None:
        overrideHelp = metric_help
    if overrideNames == None:
        overrideNames = metric_names
    if overrideLabels == None:
        overrideLabels = metric_labels
    if overrideTypes == None:
        overrideTypes = metric_type
    for i, name in enumerate(overrideNames):
        mc.addMetric(name, helpText=overrideHelp[i], metricType=overrideTypes[i])
        for j, value in enumerate(values[i]):
            if j > len(overrideLabels[i]) - 1:
                l = {}
            else:
                l = overrideLabels[i][j]
            mc.addMetric(name, value=value, labels=l)
    return mc


def test_metrics_generation():
    """metrics string generation

    Given a set of information a string in metrics file format should be provided
    """
    mc = prepareMetricsObjectForTest()
    assert str(mc) == metrics_string


def test_metric_instance_identity():
    """test if two metric instances are the same metric"""
    mc1 = prepareMetricsObjectForTest()
    v2 = copy.deepcopy(metric_values)
    v2[0].remove(19)
    mc2 = prepareMetricsObjectForTest(v2)

    # different names but same labels are never same or even equal
    c1_1 = mc1.metrics[metric_names[0]].instances[0]
    c1_2 = mc1.metrics[metric_names[2]].instances[0]

    assert not c1_1.same(c1_2)
    assert c1_1.labels == c1_2.labels

    # same name, same labels, different values
    # => same but not equal

    c2_1 = mc1.metrics[metric_names[0]].instances[1]
    c2_2 = mc2.metrics[metric_names[0]].instances[1]

    assert c2_1.value == metric_values[0][3]
    assert c2_2.value == metric_values[0][1]
    assert c2_1.same(c2_2)
    assert c2_1 != c2_2

    # ensure type difference gives `False` as result

    foo = float(1.45)

    assert not c1_1.same(foo)


def test_metric_same_label_replace_value(caplog):
    """ensure the replacement of the value if labels are same"""
    with caplog.at_level(level="DEBUG"):
        mc = prepareMetricsObjectForTest()

    assert (
        f"Update value of a `{metric_names[0]}` metric from `{metric_values[0][1]}` to `{metric_values[0][3]}`."
        in [rec.message for rec in caplog.records if rec.levelno == logging.DEBUG]
    )


def test_name_change():
    """ensure a name change is done down to all edges"""
    mc = prepareMetricsObjectForTest()
    new_name = "newMetricName"
    names = list(mc.metrics.keys())
    replace_index = 2
    old_name = names[replace_index]
    for i in range(0, 2):
        if i == 0:
            check_name = old_name
            no_name = new_name
        else:
            check_name = new_name
            no_name = old_name

        assert check_name in mc.metrics.keys()
        assert no_name not in mc.metrics.keys()

        checkSet = mc.metrics[check_name]
        assert checkSet.name == check_name

        instances = checkSet.instances
        for m in instances:
            assert m.name == check_name

        if i == 0:
            mc.renameMetrics(old_name, new_name)


def test_warning_for_new_metric_without_help(caplog):
    """ensure a warning is at least logged if metric created without help info"""
    h = copy.deepcopy(metric_help)
    check_idx = 0
    h[check_idx] = None
    with caplog.at_level(level="DEBUG"):
        mc = prepareMetricsObjectForTest(overrideHelp=h)

    assert (
        f"No help information passed for new metric `{metric_names[check_idx]}`!"
        in [rec.message for rec in caplog.records if rec.levelno == logging.WARNING]
    )


def test_logs_when_changing_type_and_help_by_adding_new_metrics(caplog):
    mc = prepareMetricsObjectForTest()
    workIdx = 0
    newType = "gauge"
    newHelp = "New Help Text"
    metricName = metric_names[workIdx]

    assert mc.metrics[metricName].type != newType
    assert mc.metrics[metricName].helpText != newHelp

    with caplog.at_level(level="DEBUG"):
        mc.addMetric(metricName, helpText=newHelp, metricType=newType)

    assert mc.metrics[metricName].type == newType
    assert mc.metrics[metricName].helpText == newHelp
    assert f"Changed help for metric `{metricName}`." in [
        rec.message for rec in caplog.records if rec.levelno == logging.INFO
    ]
    assert f"Changed type for metric `{metricName}`." in [
        rec.message for rec in caplog.records if rec.levelno == logging.WARNING
    ]


def test_debug_message_for_fallback_on_no_given_metric_type(caplog):
    """check debug notice when creating a metric without type so fallback to `gauge` is used"""
    with caplog.at_level(level="DEBUG"):
        mc = prepareMetricsObjectForTest()

    assert (
        f"Defaulting metric type to `gauge` for new created metric `{metric_names[2]}`."
        in [rec.message for rec in caplog.records if rec.levelno == logging.DEBUG]
    )


def test_error_on_metric_and_label_name_conflict(caplog):
    """check debug notice when creating a metric without type so fallback to `gauge` is used"""
    names = copy.deepcopy(metric_names)
    names[0] = f"={names[0]}"  # `=` is a non-allowed character for metric names

    labels = copy.deepcopy(metric_labels)
    wrong_label = list(labels[0][0].keys())[0]
    label_value = labels[0][0][wrong_label]
    del labels[0][0][wrong_label]
    wrong_label = f"={wrong_label}"
    labels[0][0][wrong_label] = label_value

    with caplog.at_level(level="DEBUG"):
        mc = prepareMetricsObjectForTest(overrideNames=names, overrideLabels=labels)

    errorLogs = [rec.message for rec in caplog.records if rec.levelno == logging.ERROR]
    assert (
        f'"{names[0]}" does not match the Prometheus specifications. Please adjust!'
        in errorLogs
    )
    assert (
        f'Label with name "{wrong_label}" does not match the Prometheus specifications. Please adjust!'
        in errorLogs
    )


def test_metric_count_in_set():
    """check if length calculation is working correctly"""
    mc = prepareMetricsObjectForTest()
    assert len(mc.metrics[metric_names[2]]) == len(metric_values[2])


def test_getting_metrics_instance():
    """check if getting metrics instance is working correctly"""
    mc = prepareMetricsObjectForTest()
    em = MetricsCollection.Metric.MetricInstance(
        metric_names[2], metric_values[2][1], metric_labels[2][1]
    )
    assert mc.metrics[metric_names[2]][1] == em


def test_metric_comments():
    """test additional comments in metrics"""
    mc = prepareMetricsObjectForTest()
    test_comments = [
        """This is a multiline
comment ...""",
        "This is a comment with a backslash \\ in it",
    ]
    expected_lines = [
        "# {}".format(c.replace("\\", "\\\\").replace("\n", "\\n"))
        for c in test_comments
    ]
    for comment in test_comments:
        mc.metrics[metric_names[0]].addComment(comment)
    expected_string = metrics_string.splitlines()
    expected_string[2:2] = expected_lines
    assert str(mc) == "\n".join(expected_string) + "\n"
    assert len(mc.metrics[metric_names[0]].getComments()) == len(test_comments)

    assert (
        mc.metrics[metric_names[0]].popComment(len(test_comments) - 1)
        == test_comments[len(test_comments) - 1]
    )
    assert len(mc.metrics[metric_names[0]].getComments()) == len(test_comments) - 1

    expected_string = metrics_string.splitlines()
    expected_string[2:2] = expected_lines[:-1]
    assert str(mc) == "\n".join(expected_string) + "\n"


def test_nonsense_metrics_type(caplog):
    """test fallback type on nonsense metric types"""
    types = copy.deepcopy(metric_type)
    types[2] = "nonsense"
    with caplog.at_level(level="DEBUG"):
        mc = prepareMetricsObjectForTest(overrideTypes=types)

    assert (
        f'"{types[2]}" is not a valid type, which are defined by {MetricsCollection.Metric.validMetricTypes}'
        in [rec.message for rec in caplog.records if rec.levelno == logging.ERROR]
    )
