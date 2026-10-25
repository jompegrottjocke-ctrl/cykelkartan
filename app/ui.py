import json
import sys
from pathlib import Path
from PySide6.QtCore import QObject, Signal, Slot, QRunnable, QThreadPool, QUrl, QStandardPaths, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QLineEdit,QComboBox,QSlider,QCheckBox,QListWidget,QFileDialog,QInputDialog,QMessageBox,QSplitter)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from PySide6.QtWebChannel import QWebChannel
from app.identity import APP_NAME
from app.storage import Store
from app.services import MapData
from app.routing import MODES, calculate, export_route, minutes

ROOT=Path(__file__).resolve().parent.parent
class Signals(QObject):
    done=Signal(object)
    error=Signal(str)
class Job(QRunnable):
    def __init__(self, fn):
        super().__init__(); self.fn=fn; self.signals=Signals()
    def run(self):
        try: self.signals.done.emit(self.fn())
        except Exception as e: self.signals.error.emit(str(e))
class Bridge(QObject):
    def __init__(self, window): super().__init__(); self.w=window
    @Slot()
    def ready(self):
        self.w.map_ready=True
        pos=self.w.store.get('position',[55.605,13.0038,13])
        self.w.js(f'map.setView([{pos[0]},{pos[1]}],{pos[2]})')
        self.w.work(self.w.data.load, self.w.loaded, 'Läser lokal kartdata …')
    @Slot()
    def mapError(self):
        self.w.statusBar().showMessage('Bakgrundskartan kunde inte hämtas. Kontrollera internet och karttjänstens åtkomst. Lokal ruttdata påverkas inte.')
    @Slot(str,float,float)
    def choose(self,kind,lat,lon): self.w.choose(kind,[lat,lon])
    @Slot(int,float,float)
    def moved(self,i,lat,lon):
        pts=self.w.points()
        had_route=bool(self.w.route)
        if i==0:self.w.start= [lat,lon]
        elif i==len(pts)-1:self.w.end=[lat,lon]
        else:self.w.via[i-1]=[lat,lon]
        self.w.sync()
        if had_route:self.w.compute()
    @Slot(float,float,int)
    def position(self,lat,lon,zoom): self.w.store.set('position',[lat,lon,zoom])

class Window(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle(APP_NAME); self.resize(1380,900)
        self.setWindowIcon(QIcon(str(ROOT/'assets/icons/cykel.ico')))
        directory=Path(QStandardPaths.writableLocation(QStandardPaths.AppLocalDataLocation))
        self.store=Store(directory/'settings.sqlite');self.data=MapData(directory/'map')
        self.start=None;self.end=None;self.via=[];self.route=None;self.map_ready=False;self.jobs=[];self.busy=False
        splitter=QSplitter();self.setCentralWidget(splitter)
        panel=QWidget();panel.setMinimumWidth(340);panel.setMaximumWidth(440);layout=QVBoxLayout(panel);layout.setContentsMargins(24,24,24,20);layout.setSpacing(12)
        title=QLabel('◉  Cykelfrämjandet\n     Malmö');title.setStyleSheet('font-size:24px;font-weight:700;color:#16856A');layout.addWidget(title)
        layout.addWidget(QLabel('DIN STAD. DIN VÄG.'))
        for label,attr,kind in [('Från','from_edit','start'),('Till','to_edit','end')]:
            layout.addWidget(QLabel(label));row=QHBoxLayout();edit=QLineEdit();edit.setPlaceholderText('Adress eller latitud, longitud');setattr(self,attr,edit);row.addWidget(edit)
            b=QPushButton('Sök');b.clicked.connect(lambda checked=False,k=kind,e=edit:self.search(k,e.text()));row.addWidget(b);edit.returnPressed.connect(lambda k=kind,e=edit:self.search(k,e.text()));layout.addLayout(row)
        b=QPushButton('↕  Byt start och mål');b.clicked.connect(self.swap);layout.addWidget(b)
        self.mode=QComboBox();self.mode.addItems(MODES);layout.addWidget(self.mode)
        self.detour=QComboBox();self.detour.addItems(['10 % omväg','20 % omväg','30 % omväg']);self.detour.setCurrentIndex(1);layout.addWidget(self.detour)
        self.speed_label=QLabel();layout.addWidget(self.speed_label)
        self.speed=QSlider(Qt.Horizontal);self.speed.setRange(5,40);self.speed.setValue(self.store.get('speed',15));self.speed.valueChanged.connect(self.speed_changed);layout.addWidget(self.speed)
        self.wait=QCheckBox('Räkna med uppskattad väntetid');layout.addWidget(self.wait)
        self.go=QPushButton('Beräkna cykelrutt');self.go.setObjectName('primary');self.go.clicked.connect(self.compute);layout.addWidget(self.go)
        self.summary=QLabel('Välj start och mål på kartan.\nHämta cykelvägnätet före första rutten.');self.summary.setWordWrap(True);layout.addWidget(self.summary)
        self.steps=QListWidget();self.steps.itemClicked.connect(lambda item:self.js('highlight('+json.dumps(self.route['instructions'][self.steps.row(item)]['coords'])+')') if self.route else None);layout.addWidget(self.steps,1)
        row=QHBoxLayout()
        for text,fn in [('Spara',self.save),('Sparade',self.open_saved),('Exportera',self.export)]:
            b=QPushButton(text);b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        row=QHBoxLayout()
        for text,fn in [('Kopiera',self.copy),('PNG',self.png),('Centrera',lambda:self.js('center()'))]:
            b=QPushButton(text);b.clicked.connect(fn);row.addWidget(b)
        layout.addLayout(row)
        self.theme=QCheckBox('Mörkt tema');self.theme.setChecked(self.store.get('dark',False));self.theme.toggled.connect(self.theme_changed);layout.addWidget(self.theme)
        b=QPushButton('Uppdatera cykelkartan');b.clicked.connect(self.update);layout.addWidget(b)
        splitter.addWidget(panel)
        self.web=QWebEngineView();splitter.addWidget(self.web);splitter.setSizes([390,990])
        self.web.settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls,True)
        self.channel=QWebChannel();self.bridge=Bridge(self);self.channel.registerObject('bridge',self.bridge);self.web.page().setWebChannel(self.channel)
        self.web.load(QUrl.fromLocalFile(str(ROOT/'app/maps/index.html')))
        self.speed_changed(self.speed.value());self.theme_changed(self.theme.isChecked())
        self.statusBar().showMessage('Kartplattor kräver internet. Lokal ruttberäkning fungerar efter datahämtning.')
    def js(self,code): self.web.page().runJavaScript(code)
    def work(self,fn,done,status):
        if self.busy: return
        self.busy=True;self.go.setEnabled(False);self.statusBar().showMessage(status)
        job=Job(fn);self.jobs.append(job)
        def finish():
            self.busy=False;self.go.setEnabled(True);self.jobs.remove(job)
        def success(value):
            finish();done(value)
        def failure(message):
            finish();self.statusBar().showMessage('Åtgärden misslyckades. Tidigare data behålls.');QMessageBox.warning(self,APP_NAME,message)
        job.signals.done.connect(success);job.signals.error.connect(failure);QThreadPool.globalInstance().start(job)
    def points(self): return ([self.start] if self.start else [])+self.via+([self.end] if self.end else [])
    def sync(self):
        for point,edit in [(self.start,self.from_edit),(self.end,self.to_edit)]:
            edit.setText(f'{point[0]:.6f}, {point[1]:.6f}' if point else '')
        self.route=None;self.steps.clear();self.js('line.clearLayers()');self.js('points('+json.dumps(self.points())+')')
    def choose(self,kind,p):
        if kind=='start':self.start=p
        elif kind=='end':self.end=p
        else:self.via.append(p)
        self.sync()
    def swap(self): self.start,self.end=self.end,self.start;self.via.reverse();self.sync()
    def search(self,kind,text):
        try:
            lat,lon=map(float,text.split(','))
            if not 55.4<lat<55.8 or not 12.7<lon<13.4: raise ValueError()
            self.choose(kind,[lat,lon]);return
        except ValueError: pass
        if not text.strip(): return
        def lookup():
            from osmnx import geocode
            return list(geocode(text+', Malmö, Sweden'))
        self.work(lookup,lambda p:self.choose(kind,p),'Söker adress …')
    def loaded(self,g):
        if g is None:self.statusBar().showMessage('Inget lokalt cykelvägnät. Klicka på Uppdatera cykelkartan.')
        else:self.js('infrastructure('+json.dumps(self.data.features())+')');self.statusBar().showMessage('Lokalt vägnät tillgängligt. Senast uppdaterat: '+self.store.get('updated','okänt'))
        self.js('dark('+json.dumps(self.theme.isChecked())+')')
    def update(self):
        def done(stamp):self.store.set('updated',stamp);self.loaded(self.data.graph)
        self.work(self.data.update,done,'Hämtar Malmö kommuns cykelvägnät. Detta kan ta flera minuter …')
    def compute(self):
        if self.data.graph is None:QMessageBox.information(self,APP_NAME,'Uppdatera cykelkartan för att hämta ett lokalt vägnät först.');return
        if not self.start or not self.end:QMessageBox.information(self,APP_NAME,'Välj både start och destination.');return
        args=(self.data.graph,self.points(),self.mode.currentText(),self.speed.value(),[10,20,30][self.detour.currentIndex()],self.wait.isChecked())
        self.work(lambda:calculate(*args),self.result,'Beräknar cykelrutt …')
    def result(self,r):
        self.route=r;self.js('route('+json.dumps(r['coords'])+')');self.steps.clear();self.steps.addItems([s['text'] for s in r['instructions']]);self.render_summary();self.statusBar().showMessage('Rutt beräknad från OpenStreetMap. Prioriteringar är modeller, ingen säkerhetsgaranti.')
    def render_summary(self):
        if not self.route:return
        r=self.route;r['minutes']=minutes(r['meters'],self.speed.value())
        shares=' · '.join(f'{k}: {v/r["meters"]:.0%}' for k,v in r['distribution'].items())
        self.summary.setText(f'{r["meters"]/1000:.2f} km  •  {r["minutes"]+r["wait"]:.0f} min\nCykeltid {r["minutes"]:.1f} min · Väntetid ≈ {r["wait"]:.1f} min\n{self.speed.value()} km/h · {len(r["points"])-2} mellanstopp\n{shares}')
    def speed_changed(self,value):
        self.speed_label.setText(f'Cykelhastighet   {value} km/h');self.store.set('speed',value);self.render_summary()
    def theme_changed(self,dark):
        self.store.set('dark',dark);bg='#111B19' if dark else '#F6F8F7';fg='#F3F7F5' if dark else '#182724';panel='#1B2925' if dark else '#FFFFFF'
        self.setStyleSheet(f'QWidget{{background:{bg};color:{fg};font-family:"Segoe UI";font-size:13px}} QLineEdit,QComboBox,QListWidget{{background:{panel};border:1px solid #73817c;border-radius:8px;padding:9px}} QPushButton{{background:{panel};border:1px solid #73817c;border-radius:8px;padding:10px}} QPushButton:hover{{border-color:#16856a}} QPushButton#primary{{background:#16856a;color:white;font-weight:bold;padding:14px}}')
        if self.map_ready:self.js('dark('+json.dumps(dark)+')')
    def save(self):
        if not self.route:return
        name,ok=QInputDialog.getText(self,APP_NAME,'Namn på rutten:')
        if ok and name.strip():self.store.save(name.strip(),self.route)
    def open_saved(self):
        rows=self.store.saved()
        if not rows:QMessageBox.information(self,APP_NAME,'Inga sparade rutter ännu.');return
        choices=[f'{i} · {name}' for i,name,data in rows];choice,ok=QInputDialog.getItem(self,APP_NAME,'Öppna sparad rutt:',choices,0,False)
        if ok:
            r=rows[choices.index(choice)][2];self.start=r['points'][0];self.end=r['points'][-1];self.via=r['points'][1:-1];self.sync();self.result(r)
    def export(self):
        if not self.route:return
        path,_=QFileDialog.getSaveFileName(self,APP_NAME,'cykelrutt.gpx','GPX (*.gpx);;GeoJSON (*.geojson)')
        if path:
            try:export_route(self.route,path)
            except OSError as e:QMessageBox.warning(self,APP_NAME,str(e))
    def copy(self):
        if self.route:QApplication.clipboard().setText(APP_NAME+'\n'+self.from_edit.text()+' → '+self.to_edit.text()+'\n'+self.summary.text())
    def png(self):
        path,_=QFileDialog.getSaveFileName(self,APP_NAME,'cykelkarta.png','PNG (*.png)')
        if path and not self.web.grab().save(path):QMessageBox.warning(self,APP_NAME,'Bilden kunde inte sparas.')
    def closeEvent(self,event):
        if self.busy:
            QMessageBox.information(self,APP_NAME,'Vänta tills det pågående arbetet är klart.');event.ignore()
        else:event.accept()

def run():
    app=QApplication(sys.argv);app.setApplicationName(APP_NAME);app.setOrganizationName('CykelframjandetMalmo')
    window=Window();window.show();sys.exit(app.exec())
