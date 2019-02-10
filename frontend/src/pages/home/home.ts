import {Component, ViewChild} from '@angular/core';
import {IonicPage, NavController, NavParams, Slides} from 'ionic-angular';
@IonicPage()
@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {
  image_indices: number[] = [7, 8, 9, 10];
  @ViewChild(Slides) slides: Slides;

  constructor(public navCtrl: NavController, public navParams: NavParams) {}

  ionViewDidLoad() {}

  getImageStyleURL(image_index: number) {
    return 'url("assets/imgs/home/carousel/' + image_index + '.jpg")';
  }

  goto(page: string) {
    this.navCtrl.setRoot(page);
  }
}
