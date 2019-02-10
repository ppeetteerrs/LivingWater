import { NgModule, ErrorHandler } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { IonicApp, IonicModule, IonicErrorHandler } from 'ionic-angular';
import { MyApp } from './app.component';
import { AddVersePageModule } from "../pages/add-verse/add-verse.module"

import { StatusBar } from '@ionic-native/status-bar';
import { SplashScreen } from '@ionic-native/splash-screen';
import { Clipboard } from "@ionic-native/clipboard";
import { HttpClientModule } from "@angular/common/http";
import { ElectronProvider } from '../providers/electron/electron';
import { HttpProvider } from '../providers/http/http';
import { BibleBookListProvider } from '../providers/bible-book-list/bible-book-list';

@NgModule({
  declarations: [
    MyApp
  ],
  imports: [
    BrowserModule,
    IonicModule.forRoot(MyApp),
    HttpClientModule,
    AddVersePageModule
  ],
  bootstrap: [IonicApp],
  entryComponents: [
    MyApp
  ],
  providers: [
    StatusBar,
    SplashScreen,
    {provide: ErrorHandler, useClass: IonicErrorHandler},
    ElectronProvider,
    HttpProvider,
    Clipboard,
    BibleBookListProvider
  ]
})
export class AppModule {}
