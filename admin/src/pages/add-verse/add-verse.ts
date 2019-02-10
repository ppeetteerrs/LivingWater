import { Component } from "@angular/core";
import {
  IonicPage,
  NavController,
  NavParams,
  ToastController,
  ViewController
} from "ionic-angular";
import { HttpProvider } from "../../providers/http/http";

@IonicPage()
@Component({
  selector: "page-add-verse",
  templateUrl: "add-verse.html"
})
export class AddVersePage {
  keyword_items: { word: string; level: number }[] = [];
  verse_location: string = "";
  keyword_input: string = "";
  keyword_level_input: string = "";

  constructor(
    public navCtrl: NavController,
    public navParams: NavParams,
    public toastCtrl: ToastController,
    public http: HttpProvider,
    public viewCtrl: ViewController
  ) {}

  submitKeyword() {
    let parsed_level = parseInt(this.keyword_level_input);
    if (
      !Number.isInteger(parsed_level) ||
      parsed_level > 3 ||
      parsed_level < 1
    ) {
      this.presentToast("Level must be 1 or 2 or 3");
    } else if (this.keyword_input == "") {
      this.presentToast("You are lucky I caught ur misclick =.=");
    } else {
      this.keyword_items.push({
        word: this.keyword_input,
        level: parsed_level
      });
      this.keyword_items.sort((a, b) => {
        return a.level - b.level;
      });
      this.keyword_level_input = "";
      this.keyword_input = "";
    }
  }

  deleteItem(keyword_item: { word: string; level: number }) {
    let item_index = this.keyword_items.indexOf(keyword_item);
    this.keyword_items = this.keyword_items.filter((item, index, arr) => {
      return index != item_index;
    });
    this.keyword_items.sort((a, b) => {
      return a.level - b.level;
    });
  }

  presentToast(message: string) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 7000
    });
    toast.present();
  }

  addVerse() {
    if (this.verse_location == "") {
      this.presentToast("Haiiiiiizzzzz");
    } else if (this.keyword_items.length == 0) {
      this.presentToast("That's not funny.....");
    } else {
      let lvl1: string[] = [];
      let lvl2: string[] = [];
      let lvl3: string[] = [];
      this.keyword_items.forEach((item, index, arr) => {
        if (item.level == 1) {
          lvl1.push(item.word);
        } else if (item.level == 2) {
          lvl2.push(item.word);
        } else {
          lvl3.push(item.word);
        }
      });
      this.viewCtrl.dismiss(
        this.http.addVerse(this.verse_location, lvl1, lvl2, lvl3)
      );
    }
  }
}
