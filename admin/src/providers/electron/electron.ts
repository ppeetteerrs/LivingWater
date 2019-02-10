import { Injectable } from '@angular/core';
import * as electron from 'electron';

@Injectable()
export class ElectronProvider {
  currentZoom: number = 0;
  constructor() {

  }
  zoomIn(){
    electron.webFrame.setZoomLevel(++this.currentZoom);
  }
  zoomOut(){
    electron.webFrame.setZoomLevel(--this.currentZoom);
  }

}
