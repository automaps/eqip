"""
 eqip

                              -------------------
        begin                : 2022-05-23
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Alexandra Institute
        email                : christian.heider@alexandra.dk

"""

import logging
import warnings

# noinspection PyUnresolvedReferences
from qgis.core import QgsSettings

# noinspection PyUnresolvedReferences
from qgis.gui import QgisInterface

# noinspection PyUnresolvedReferences
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QTranslator

from eqip import PLUGIN_DIR, PROJECT_NAME

MENU_INSTANCE_NAME = f"&{PROJECT_NAME.lower()}"

DEBUGGING_PORT = 6969

VERBOSE = False
DEBUGGING = False
FORCE_RELOAD = False

logger = logging.getLogger(__name__)

if True:  # BOOTSTRAPPING EQIP ITSELF
    from .configuration.pip_parsing import get_requirements_from_file
    from .configuration.piper import (
        install_requirements_from_name,
        is_package_updatable,
    )

    UPDATABLE_REQS = [
        req.name
        for req in get_requirements_from_file(PLUGIN_DIR / "requirements.txt")
        if is_package_updatable(req.name)
    ]

    if UPDATABLE_REQS:
        install_requirements_from_name(*UPDATABLE_REQS, upgrade=True)
        if FORCE_RELOAD:
            for u in UPDATABLE_REQS:
                from warg import reload_module

                logger.info(f"reloading module {u}")
                reload_module(u)

    # noinspection PyUnresolvedReferences
    from .resources import *  # Initialize Qt resources from file resources.py # TODO: MAKE AN ASSERT ON THIS BEING IMPORTED? maybe add to devpack dev-tools

    assert qt_resource_data is not None


class EqipPlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface: QgisInterface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        self.iface = iface  # Save reference to the QGIS interface
        self.plugin_dir = PLUGIN_DIR

        locale = QgsSettings().value(
            f"{PROJECT_NAME}/locale/userLocale", QLocale().name()
        )

        IGNORE = """if DEBUGGING:
            import pydevd_pycharm

            pydevd_pycharm.settrace(
                "localhost",
                port=DEBUGGING_PORT,
                stdoutToServer=True,
                stderrToServer=True,
            )
        """

        if isinstance(locale, str):
            locale = locale[0:2]  # locale == "en"
            locale_path = self.plugin_dir / "i18n" / f"{PROJECT_NAME}_{locale}.qm"

            if locale_path.exists():
                self.translator = QTranslator()
                self.translator.load(str(locale_path))
                QCoreApplication.installTranslator(self.translator)
        else:
            warnings.warn(
                f"Unable to determine locale for {PROJECT_NAME} was {type(locale)} {locale}"
            )

        self.menu = self.tr(MENU_INSTANCE_NAME)

        from .configuration.options import EqipOptionsPageFactory
        from .configuration.project_settings import DEFAULT_PROJECT_SETTINGS
        from .configuration.settings import read_project_setting

        self.options_factory = EqipOptionsPageFactory()

        if True:
            if read_project_setting(
                "AUTO_ENABLE_DEP_HOOK",
                defaults=DEFAULT_PROJECT_SETTINGS,
                project_name=PROJECT_NAME,
            ):
                from .plugins.hook import add_plugin_dep_hook

                add_plugin_dep_hook()

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        # self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(PROJECT_NAME, message)

    def initGui(self):
        self.options_factory.setTitle(self.tr(PROJECT_NAME))
        self.iface.registerOptionsWidgetFactory(self.options_factory)

    def unload(self):
        self.iface.unregisterOptionsWidgetFactory(self.options_factory)
        del self.options_factory
