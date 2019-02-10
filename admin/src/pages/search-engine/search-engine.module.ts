import { NgModule } from '@angular/core';
import { IonicPageModule } from 'ionic-angular';
import { SearchEnginePage } from './search-engine';

@NgModule({
  declarations: [
    SearchEnginePage,
  ],
  imports: [
    IonicPageModule.forChild(SearchEnginePage),
  ],
})
export class SearchEnginePageModule {}
