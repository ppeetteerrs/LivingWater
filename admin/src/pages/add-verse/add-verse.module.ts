import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { AddVersePage } from './add-verse';

@NgModule({
  declarations: [
    AddVersePage,
  ],
  imports: [
    IonicPageModule.forChild(AddVersePage),
  ],
})
export class AddVersePageModule {}
