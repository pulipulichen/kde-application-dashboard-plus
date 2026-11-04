# Desktop acceptance checks (Kubuntu 24.04 / Plasma 5.27 / X11)

1. Confirm Chinese input works in another Qt application with the same IME.
2. Add Plus to two panels, preferably on separate screens. Open one: the visible
   search field should have a cursor immediately.
3. Compose a Chinese query with several syllables. Preedit text and candidates
   should be visible. Space/Enter must select a candidate without starting an app.
   Continue composing while results arrive: the editor must keep focus.
4. Paste Chinese text; clear it with the clear button; enter English and mixed
   Chinese/English queries. Existing KRunner matching determines available results.
5. Press Down or Tab, navigate results, and press Enter to launch. Reopen, type
   a query, then press Enter directly in the editor to launch the first result.
   Return from the first row using Up, then switch to Chinese input again.
6. Open instance A, then instance B: only B may remain visible. Repeat rapidly.
7. Open A on desktop 1, switch to desktop 2: A closes. Open B, return to desktop
   1, reopen A: no old window should remain or pull you to another desktop.
8. Repeat on both screens; the dashboard must use the launching panel's screen.
9. Verify favorites, categories, widget adding, context menus and the configured
   launcher keyboard shortcut. Check desktop/vertical-panel placement if used.
10. Verify Escape cancels composition first, then clears a committed query, then
    closes the launcher. Verify the original KDE launcher remains available.
11. Check UI in en_US, zh_TW, zh_CN and ja_JP. Update and log out/in before testing
    a changed native binary. Remove only Plus with uninstall.sh.

Automated IME tests inject Qt preedit/commit events; they cannot certify an actual
Fcitx/IBus candidate popup or the user's environment variables and IME modules.
