// SPDX-License-Identifier: GPL-3.0-or-later
#include <QQmlExtensionPlugin>
#include <qqml.h>
#include "dashboardwindow.h"
class DashboardPlusPlugin : public QQmlExtensionPlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID QQmlExtensionInterface_iid)
public:
    void registerTypes(const char *uri) override { qmlRegisterType<DashboardWindow>(uri, 1, 0, "DashboardWindow"); }
};
#include "plugin.moc"
