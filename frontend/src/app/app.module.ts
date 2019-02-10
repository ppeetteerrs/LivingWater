import { BrowserModule } from "@angular/platform-browser";
import { ErrorHandler, NgModule } from "@angular/core";
import { IonicApp, IonicErrorHandler, IonicModule } from "ionic-angular";
import { HttpModule } from "@angular/http";
import { MyApp } from "./app.component";
import { StatusBar } from "@ionic-native/status-bar";
import { SplashScreen } from "@ionic-native/splash-screen";
import { Clipboard } from "@ionic-native/clipboard";
import { LocalVersesProvider } from '../providers/local-verses/local-verses';
import { BibleBookListProvider } from '../providers/bible-book-list/bible-book-list';

@NgModule({
  declarations: [MyApp],
  imports: [BrowserModule, HttpModule, IonicModule.forRoot(MyApp)],
  bootstrap: [IonicApp],
  entryComponents: [MyApp],
  providers: [
    StatusBar,
    SplashScreen,
    Clipboard,
    { provide: ErrorHandler, useClass: IonicErrorHandler },
    LocalVersesProvider,
    BibleBookListProvider
  ]
})
export class AppModule {}
