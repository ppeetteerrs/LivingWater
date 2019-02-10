import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { VerseListPage } from './verse-list';
import { ComponentsModule } from "../../components/components.module"

@NgModule({
  declarations: [
    VerseListPage,
  ],
  imports: [
    IonicPageModule.forChild(VerseListPage),
    ComponentsModule
  ],
})
export class VerseListPageModule {}
