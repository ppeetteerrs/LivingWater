import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { OccasionsPage } from './occasions';

@NgModule({
  declarations: [
    OccasionsPage,
  ],
  imports: [
    IonicPageModule.forChild(OccasionsPage),
  ],
})
export class OccasionsPageModule {}
