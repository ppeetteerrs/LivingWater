import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';
import { LocalVersesProvider } from '../../providers/local-verses/local-verses';

@IonicPage()
@Component({
  selector: 'page-occasions',
  templateUrl: 'occasions.html',
})
export class OccasionsPage {

  occasions;
  display_occasions;
  searchInput: string;

  constructor(public navCtrl: NavController, public navParams: NavParams, public verses: LocalVersesProvider) {
    this.occasions = Object.keys(verses.occasions_data);
    this.display_occasions = this.occasions;
  }

  localSearch() {
    this.display_occasions = this.verses.localSearch(this.searchInput, this.occasions);
  }

  openOccasion(occasion: string) {
    this.navCtrl.push("VerseListPage", {title: occasion, data: this.verses.occasions_data[occasion]})
  }

}
