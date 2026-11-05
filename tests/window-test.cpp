// SPDX-License-Identifier: GPL-3.0-or-later
#include <QtTest>
#include <QGuiApplication>
#include <QQmlComponent>
#include <QQmlEngine>
#include <QQuickItem>
#include <QQuickWindow>
#include <QInputMethodEvent>
#include <QTemporaryDir>
#include <QFile>
#include <memory>

class WindowTest : public QObject {
    Q_OBJECT
    std::unique_ptr<QObject> makeWindow(QQmlEngine &engine) {
        QQmlComponent c(&engine);
        c.setData(QByteArray("import QtQuick 2.15\nimport \"") + QUrl::fromLocalFile(NATIVE_IMPORT_DIR).toEncoded() + "\" 1.0 as Plus\n"
            "Plus.DashboardWindow { id: win; width: 500; height: 300;"
            " property alias text: editor.text; property alias preedit: editor.preeditText;"
            " property alias firstFavorite: favorite; property alias searchEditor: editor;"
            " keyEventProxy: editor; mainItem: FocusScope { width: win.width; height: win.height; focus: true;"
            " Item { id: favorite; focus: true; Keys.onRightPressed: event => { event.accepted = true; } }"
            " TextInput { id: editor; width: 400; height: 60 } } }", QUrl::fromLocalFile("/test.qml"));
        for (int i = 0; c.isLoading() && i < 500; ++i) QTest::qWait(10);
        auto result = std::unique_ptr<QObject>(c.create());
        if (!result) qWarning() << c.errors();
        return result;
    }
    void toggle(QObject *w) { QVERIFY(QMetaObject::invokeMethod(w, "toggle")); }
private Q_SLOTS:

    void dynamicDashboardWindowProperty() {
        // Regression: a QML-derived native window created dynamically could
        // not be assigned to a strictly typed DashboardWindow property in Qt 5.
        QTemporaryDir directory;
        QVERIFY(directory.isValid());
        QFile child(directory.filePath("DashboardDerived.qml"));
        QVERIFY(child.open(QIODevice::WriteOnly));
        const QByteArray childSource = QByteArray("import QtQuick 2.15\nimport \"")
            + QUrl::fromLocalFile(NATIVE_IMPORT_DIR).toEncoded()
            + "\" 1.0 as DashboardPlus\nDashboardPlus.DashboardWindow { }\n";
        QCOMPARE(child.write(childSource), qint64(childSource.size()));
        child.close();

        QQmlEngine engine;
        QQmlComponent parentComponent(&engine);
        const QByteArray parentSource = QByteArray("import QtQuick 2.15\nItem {\n"
            " readonly property Component dashWindowComponent: Qt.createComponent(\"")
            + QUrl::fromLocalFile(child.fileName()).toEncoded()
            + "\")\n"
            " readonly property var dashWindow: dashWindowComponent && dashWindowComponent.status === Component.Ready "
            "? dashWindowComponent.createObject(this) : null\n}\n";
        parentComponent.setData(parentSource, QUrl::fromLocalFile(directory.filePath("TestParent.qml")));
        for (int i = 0; parentComponent.isLoading() && i < 500; ++i) QTest::qWait(10);
        QVERIFY2(parentComponent.isReady(), qPrintable(parentComponent.errorString()));
        std::unique_ptr<QObject> parent(parentComponent.create());
        QVERIFY2(parent, qPrintable(parentComponent.errorString()));
        QObject *window = parent->property("dashWindow").value<QObject *>();
        QVERIFY2(window, "Dynamically created QML DashboardWindow must be assignable to var");
        QVERIFY(qobject_cast<QQuickWindow *>(window));
    }
    void dashboardComponentLoads() {
        QQmlEngine engine;
        QQmlComponent c(&engine, QUrl::fromLocalFile(DASHBOARD_QML_PATH));
        for (int i = 0; c.isLoading() && i < 500; ++i) QTest::qWait(10);
        QVERIFY2(c.isReady(), qPrintable(c.errorString()));
    }
    void oneWindowAcrossEngines() {
        QQmlEngine e1, e2;
        auto a = makeWindow(e1), b = makeWindow(e2);
        QVERIFY(a); QVERIFY(b);
        auto wa = qobject_cast<QQuickWindow *>(a.get());
        auto wb = qobject_cast<QQuickWindow *>(b.get());
        toggle(a.get()); QVERIFY(wa->isVisible());
        toggle(b.get()); QVERIFY(wb->isVisible()); QVERIFY(!wa->isVisible());
        toggle(b.get()); QVERIFY(!wb->isVisible());
        wa->show(); QVERIFY(wa->isVisible());
        wb->show(); QVERIFY(wb->isVisible()); QVERIFY(!wa->isVisible());
        b.reset(); // Deleting the owner must not leave a stale global pointer.
        toggle(a.get()); QVERIFY(wa->isVisible());
    }
    void desktopChangeCloses() {
        QQmlEngine e;
        auto a = makeWindow(e); QVERIFY(a);
        auto w = qobject_cast<QQuickWindow *>(a.get());
        toggle(a.get()); QVERIFY(w->isVisible());
        QVERIFY(QMetaObject::invokeMethod(a.get(), "closeForDesktopChange"));
        QVERIFY(!w->isVisible());
        toggle(a.get()); QVERIFY(w->isVisible());
    }
    void initialFavoriteFocusAndTyping() {
        QQmlEngine e;
        auto a = makeWindow(e); QVERIFY(a);
        auto w = qobject_cast<QQuickWindow *>(a.get());
        auto favorite = a->property("firstFavorite").value<QQuickItem *>();
        auto editor = a->property("searchEditor").value<QQuickItem *>();
        QVERIFY(favorite); QVERIFY(editor);
        toggle(a.get());
        QTRY_COMPARE(w->activeFocusItem(), favorite);
        // Arrow keys navigate the favorite rather than activating the search box.
        QTest::keyClick(w, Qt::Key_Right);
        QCOMPARE(w->activeFocusItem(), favorite);
        QTest::keyClick(w, Qt::Key_A);
        QCOMPARE(w->activeFocusItem(), editor);
        QCOMPARE(a->property("text").toString(), QStringLiteral("a"));
    }
    void chineseCompositionAndFocus() {
        QQmlEngine e;
        auto a = makeWindow(e); QVERIFY(a);
        auto w = qobject_cast<QQuickWindow *>(a.get());
        toggle(a.get());
        auto editor = a->property("searchEditor").value<QQuickItem *>();
        QVERIFY(editor);
        editor->forceActiveFocus();
        QTRY_COMPARE(w->activeFocusItem(), editor);
        QInputMethodEvent preedit(QString::fromUtf8("ㄓㄨㄥ"), {});
        QCoreApplication::sendEvent(editor, &preedit);
        QCOMPARE(a->property("text").toString(), QString());
        QCOMPARE(a->property("preedit").toString(), QString::fromUtf8("ㄓㄨㄥ"));
        QInputMethodEvent commit;
        commit.setCommitString(QString::fromUtf8("中文"));
        QCoreApplication::sendEvent(editor, &commit);
        QCOMPARE(a->property("text").toString(), QString::fromUtf8("中文"));
        QVERIFY(editor->hasActiveFocus());
        // Typing after grid navigation moves focus to the real search editor.
        auto favorite = a->property("firstFavorite").value<QQuickItem *>();
        QVERIFY(favorite);
        favorite->forceActiveFocus();
        QTest::keyClick(w, Qt::Key_A);
        QCOMPARE(w->activeFocusItem(), editor);
        QCOMPARE(a->property("text").toString(), QString::fromUtf8("中文a"));
    }
};
int main(int argc, char **argv) {
    QGuiApplication app(argc, argv);
    WindowTest test;
    return QTest::qExec(&test, argc, argv);
}
#include "window-test.moc"
