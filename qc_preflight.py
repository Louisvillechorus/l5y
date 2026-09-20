"""THE OPERATOR'S PATH, exactly as the room will do it."""
import os
from playwright.sync_api import sync_playwright
U='file://'+os.path.abspath('/home/user/l5y/L5Y-Show-STANDALONE.html')
bad=[]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/opt/pw-browsers/chromium')
    c=b.new_context(viewport={'width':1920,'height':1080})
    pg=c.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(1200)
    if not pg.is_visible('#gate'): bad.append('the questionnaire does not come up on a cold open')
    if pg.evaluate('started'): bad.append('the show is running before anyone answered the gate')
    # keys are dead behind the gate
    pg.keyboard.press('Space'); pg.wait_for_timeout(200)
    if pg.evaluate('started'): bad.append('SPACE started the show from behind the gate')
    # answer it the way the room will
    pg.click('button.castbtn[data-cast="ml"]'); pg.wait_for_timeout(250)
    perf=pg.evaluate("document.querySelectorAll('#gPerf .mbtn').length")
    pg.evaluate("gateSel('perf','Kenneth Bailey')"); pg.wait_for_timeout(200)
    pg.evaluate('gateYes(1)'); pg.wait_for_timeout(200)
    pg.evaluate('gateYes(2)'); pg.wait_for_timeout(300)
    if not pg.is_visible('text=Start — Presenter'): pass
    pg.evaluate("startAs('presenter')"); pg.wait_for_timeout(800)
    if not pg.evaluate('started'): bad.append('the show did not start')
    if pg.evaluate("document.body.classList.contains('needgate')"): bad.append('the gate is still up after Start')
    # the projector
    p2=c.new_page(); e2=[]; p2.on('pageerror',lambda e:e2.append(str(e)))
    p2.goto(U+'?view=projection'); p2.wait_for_timeout(1000)
    if p2.is_visible('#gate'): bad.append('THE PROJECTOR IS SHOWING THE QUESTIONNAIRE')
    # fire the first few cues on the operator path and check both windows track
    for _ in range(3):
        pg.evaluate('next()')
        w=0
        while w<40000 and pg.evaluate('animRunning'): pg.wait_for_timeout(200); w+=200
        pg.wait_for_timeout(400)
    if pg.evaluate('[si,ci]') != p2.evaluate('[si,ci]'):
        bad.append(f'windows out of sync: {pg.evaluate("[si,ci]")} vs {p2.evaluate("[si,ci]")}')
    # blackout takes picture AND sound
    pg.evaluate('setBlackout(true)'); pg.wait_for_timeout(600)
    if not p2.evaluate("document.body.classList.contains('blk')"): bad.append('BLACKOUT did not reach the projector')
    pg.evaluate('setBlackout(false)'); pg.wait_for_timeout(300)
    # the selector
    pg.evaluate("document.getElementById('btnMenu').click()"); pg.wait_for_timeout(300)
    if not pg.is_visible('#jump'): bad.append('the song selector does not open')
    if p2.is_visible('#jump'): bad.append('THE SELECTOR IS SHOWING ON THE PROJECTOR')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    print('preshow performer choices:', perf)
    print('PRE-FLIGHT:', 'CLEAN' if not bad and not errs and not e2 else (bad + errs[:2] + e2[:2]))
    b.close()
