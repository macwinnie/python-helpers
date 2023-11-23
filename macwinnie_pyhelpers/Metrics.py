#!/usr/bin/env python3
import logging
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

logger = logging.getLogger(__name__)


class MetricsCollection:
    """Prometheus like metrics collection

    This class handles a collection of metrics not necessarily of the same metric name.
    """

    class Metric:
        """Collection of metrics of the same name

        Set of metrics of the same name with multiple instances, differenciated by the set labels
        """

        class MetricInstance:
            """single metric

            This is a single representation of one metric.
            """

            def __init__(self, name, value, labels={}):
                """initialize the metric instance

                Args:
                    value (mixed): actual value of the metric instance
                    labels (dict): set of labels for the metric instance (default: `{}`)
                """
                self.setName(name)
                self.setValue(value)
                self.labels = labels

            def __eq__(self, other):
                """check equality even down to the metrics value

                Args:
                    other (MetricInstance): metric instance to compare with
                """
                return self.same(other) and self.value == other.value

            def setName(self, name):
                """set / change name

                Args:
                    name (str): name to be set
                """
                self.name = name

            def setValue(self, value):
                """set / change value

                Args:
                    value (mixed / number): value to be set for Metric
                """
                self.value = value

            def same(self, other):
                """check if metric instance equals other metric instance

                ATTENTION: this method does not (!) compare the actual value of the instance.
                It only checks in the manner of Prometheus metrics if the instances have the same
                set of labels and if so, they are assumed to be equal, so the new metric can replace
                the old one.

                Args:
                    other (MetricInstance): metric instance to compare with

                Returns:
                    bool: `True` if label set is same, `False` if not or other typed object given.
                """
                if type(self) == type(other):
                    return (self.labels == other.labels) and (self.name == other.name)
                else:
                    return False

        def __init__(self, name, helpText=None, metricType="gauge"):
            """initialize Metric by name

            Args:
                name (str): name of metric to be used
                helpText (str): short description about the metric identified by name
                metricType (str): type of metric to be used (default: `gauge`)
            """
            self.instances = []
            self.setName(name)
            self.setHelp(helpText)
            self.setType(metricType)

        def setName(self, name):
            """change name

            Args:
                name (str): name to change the metrics to
            """
            self.name = name
            for i in self.instances:
                i.setName(name)

        def setHelp(self, helpText):
            """change help information about metric

            Args:
                helpText (str): help information about the metrics
            """
            self.helpText = helpText

        def setType(self, metricType):
            """change metric type

            Args:
                metricType (str): type to change metric to
            """
            self.type = metricType

        def addMetric(self, value, labels={}):
            """add a metric instance

            Only a single metric with the same label set can be contained, so
            those “duplicates” will overwrite existing ones.

            Args:
                value (mixed): value of metric instance
                labels (mixed): labels that will identify instance
            """
            m = self.MetricInstance(self.name, value, labels)
            valueChanged = False
            for i, e in enumerate(self.instances):
                if e.same(m):
                    logger.debug(
                        f"Update value of a `{self.name}` metric from `{e.value}` to `{value}`."
                    )
                    e.setValue(value)
                    valueChanged = True
                    break
            if not valueChanged:
                self.instances.append(m)

        def representation(self):
            """get directory representation for further work with metrics

            Returns:
                dict: representation of metrics
            """
            return {
                self.name: {
                    "type": self.type,
                    "help": self.helpText,
                    "instances": self.instances,
                }
            }

    def __init__(self):
        """create set of metrics"""
        self.metrics = {}

    def addMetric(
        self, metricName, value=None, labels={}, helpText=None, metricType=None
    ):
        """add a (new) metric instance

        Args:
            metricName (str): name of metric to be added
            value (mixed): value of actual metric set (default: `None`)
            labels (dict): labels to be set for actual metric set – they identify a metric! (default: `{}`)
            helpText (str): help information for the metric collection of name metricName (default: `None`)
            metricType (str): type of metric to be used – see https://prometheus.io/docs/concepts/metric_types/
                              (default: None, will default to `gauge` on creation)
        """
        if not metricName in self.metrics:
            if metricType == None:
                metricType = "gauge"
                logger.debug(
                    f"Defaulting metric type to `{metricType}` for new created metric `{metricName}`."
                )
            if helpText == None:
                logger.warning(
                    f"No help information passed for new metric `{metricName}`!"
                )
            self.metrics[metricName] = self.Metric(
                name=metricName, helpText=helpText, metricType=metricType
            )
            logger.debug(f"Added new metric `{metricName}`")
        else:
            if helpText != None:
                self.setHelp(metricName, helpText)
                logger.info(f"Changed help for metric `{metricName}`.")
            if metricType != None:
                self.setType(metricName, metricType)
                logger.warning(f"Changed type for metric `{metricName}`.")
        if value != None:
            self.metrics[metricName].addMetric(value, labels)

    def renameMetrics(self, old_name, new_name):
        """rename a bunch of metrics

        Args:
            old_name (str): old name to be renamed
            new_name (str): new name to be used
        """
        self.metrics[old_name].setName(new_name)
        self.metrics[new_name] = self.metrics[old_name]
        self.metrics.pop(old_name)

    def setHelp(self, metricName, helpText):
        """change help for metric

        Args:
            metricName (str): name of metric to set the help information
            helpText (str): help information about what the metric is to say
        """
        self.metrics[metricName].setHelp(helpText)

    def setType(self, metricName, metricType="gauge"):
        """change metric type

        Args:
            metricName (str): name of metric to set type for
            metricType (str): type to be set for metric (default: `"gauge"`)
        """
        self.metrics[metricName].setType(metricType)

    def prepare(self):
        """Helper function to transform list of metric objects of class above into usable object

        Returns:
            dict: dictionary to be pushed into template of this module to be rendered
        """
        finalized = {}
        for m in self.metrics.values():
            finalized.update(m.representation())
        return finalized

    def __str__(self):
        """string representation

        The string representation of a metrics collection is meant to be fetched by
        Prometheus or to be pushed to a Prometheus Push Gateway.

        Returns:
            str: prometheus metrics data
        """
        file_loader = FileSystemLoader(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "tpl")
        )
        env = Environment(loader=file_loader)
        template = env.get_template("metrics.j2")

        output = template.render(metrics=self.prepare()).strip() + "\n"
        return output
