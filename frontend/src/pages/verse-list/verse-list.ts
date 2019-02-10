import { Component } from '@angular/core';
import { IonicPage, NavController, NavParams } from 'ionic-angular';

@IonicPage()
@Component({
  selector: 'page-verse-list',
  templateUrl: 'verse-list.html',
})
export class VerseListPage {

  title:string;
  display_title: string;
  data: any;
  display_data: any[];
  chinese: boolean = false;

  constructor(public navCtrl: NavController, public navParams: NavParams) {
    this.title = navParams.get("title");
    this.data = navParams.get("data");
    this.display_title = this.data.title;
    this.display_data = this.formatContent(this.data.content);
  }

  toggleChinese(value: boolean) {
    this.chinese = value;
    if(this.chinese) {
      this.display_data = this.formatContent(this.data.chinese_content);
    } else {
      this.display_data = this.formatContent(this.data.content);
    }
  }

  formatContent(content_array: any[]){
    content_array.map((item, index, arr) => {
      item.content = item.content.replace(/([0-9]+ *)/g,"$1".trim().sup());
    });
    return content_array;
  }

}
