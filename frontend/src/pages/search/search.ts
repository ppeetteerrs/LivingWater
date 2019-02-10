import { Component } from "@angular/core";
import {
  NavController,
  LoadingController,
  ToastController,
  AlertController,
  IonicPage
} from "ionic-angular";
import { Http } from "@angular/http";
import "rxjs";
import { SETTINGS } from "../../app/settings";
import { Clipboard } from "@ionic-native/clipboard";
import { BibleBookListProvider } from "../../providers/bible-book-list/bible-book-list";
@IonicPage()
@Component({
  selector: "page-search",
  templateUrl: "search.html"
})
export class SearchPage {
  input_sentence: string = "";

  current_sentence: string = "";

  time_taken: number = 0;

  results: any[];

  new_version: boolean = true;

  bible_versions: any[] = [
    {
      display_title: "NIV",
      version_name: "niv"
    },
    {
      display_title: "和合本",
      version_name: "cuv"
    }
  ];

  selected_version_name: string = "niv";

  constructor(
    public navCtrl: NavController,
    public loadingCtrl: LoadingController,
    public http: Http,
    public alertCtrl: AlertController,
    public toastCtrl: ToastController,
    private clipboard: Clipboard,
    private bibleBooks: BibleBookListProvider
  ) {}

  presentToast(message: string) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 7000
    });
    toast.present();
  }

  async search(sentence, load) {
    this.results = [];

    if (sentence == "") {
      this.presentToast("What do you expect from a blank line... zzzzzzzz");
      return false;
    }

    let loading;

    if (load) {
      loading = this.loadingCtrl.create({
        content: "Please wait..."
      });

      loading.present();
    }

    this.current_sentence = sentence;
    try {
      let response = await this.http
        .get(SETTINGS.base_url + "/get_rankings", {
          params: {
            sentence: this.current_sentence,
            new_version: this.new_version
          }
        })
        .map(res => {
          console.log(res.json());
          return res.json();
        })
        .toPromise();

      this.time_taken = response.time_taken;

      this.results = response.results.map((item, index, arr) => {
        item.ranking = index + 1;
        item.expand = false;
        item.total_score = parseFloat(item.verse_score).toFixed(2);
        item.book_name = item.verse_book;
        item.book_index = this.bibleBooks.getBookIndex(item.book_name);
        for (let breakdown_item of item.base_word_breakdowns) {
          //breakdown_item.breakdown = breakdown_item.breakdown;
          breakdown_item.rounded_score = parseFloat(
            breakdown_item.best_match_score
          ).toFixed(2);
        }

        item.parsed_text = this.parseVerseText(item);

        return item;
      });

      this.results.sort((a, b) => {
        if (a.book_index < 0) {
          console.log(a.book_name);
        }
        if (b.book_index < 0) {
          console.log(b.book_name);
        }

        return b.verse_score - a.verse_score || a.book_index - b.book_index;
      });

      //Reorder rankings
      this.results.map((item, index, arr) => {
        item.ranking = index + 1;
      });

      //console.log(this.results);

      if (load) {
        loading.dismiss();
      }

      //console.log(this.results);
    } catch (e) {
      if (load) {
        loading.dismiss();
      }
      console.log(e);
      this.presentToast(e._body);
    }
  }

  async vote(result_item, positive: boolean) {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    try {
      loading.present();

      console.log(positive);
      let response = await this.http
        .get(SETTINGS.base_url + "/vote", {
          params: {
            json_string: JSON.stringify(result_item),
            positive: JSON.stringify(positive),
            new_version: this.new_version
          }
        })
        .map(res => res.json())
        .toPromise();
      if (response == "Done") {
        await this.search(this.current_sentence, false);
        loading.dismiss();
      }
    } catch (e) {
      loading.dismiss();
      console.log(e);
      this.presentToast(e._body);
    }
  }

  parseVerseText(item: any) {
    // Create response object
    let response = {};
    let verse_text = item.verse_text;
    for (let version of Object.keys(verse_text)) {
      // Create a text for every version
      response[version] = "";
      for (let chapter of Object.keys(verse_text[version])) {
        // Parse the text for each chapter
        let chapter_text = "";
        for (let verse of Object.keys(verse_text[version][chapter])) {
          if (!(
            (chapter == item.start_chapter &&
              parseInt(verse) < parseInt(item.start_verse)) ||
            (chapter == item.end_chapter &&
              parseInt(verse) > parseInt(item.end_verse))
          )) {
            chapter_text += this.cleanAndFormatText(
              verse,
              verse_text[version][chapter][verse]
            );
          }
        }

        if (Object.keys(verse_text[version]).length == 1) {
          //No need to add in chapter info if only one chapter is spanned
          response[version] = chapter_text.trim();
        } else {
          response[version] +=
            chapter.trim().bold() + " " + chapter_text.trim() + "\n";
        }
      }
      if (Object.keys(verse_text[version]).length > 1) {
        console.log(response[version]);
      }
    }
    return response;
  }

  cleanAndFormatText(verse_number: string, verse_text: string) {
    //Tidy verses
    //verse = verse.replace(/Chapter [0-9]*: */g, "");
    //verse = verse.replace(/([0-9]+ *)/g,"$1".trim().sup());
    verse_number = verse_number.trim().sup();
    verse_text = verse_text.trim();

    let formatted_text = " " + verse_number + " " + verse_text;

    return formatted_text;
  }

  popupReset() {
    const alert = this.alertCtrl.create({
      title: "Are you sure?",
      buttons: [
        {
          text: "Confirm",
          handler: data => {
            this.reset();
          }
        },
        {
          text: "Cancel",
          role: "cancel",
          handler: data => {}
        }
      ]
    });
    alert.present();
  }

  async reset() {
    let loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    try {
      loading.present();

      let response = await this.http
        .get(SETTINGS.base_url + "/reset_secrett")
        .map(res => res.json())
        .toPromise();

      if (response == "Completed") {
        await this.search(this.current_sentence, false);
        loading.dismiss();
        this.presentToast("All Votes Reset");
      }
    } catch (e) {
      loading.dismiss();
      console.log(e);
      this.presentToast(e._body);
    }
  }

  copyVerse(result_item) {
    this.clipboard.copy(result_item.location + "\n" + result_item.text);
  }

  chooseVersion(version_name: string) {
    this.selected_version_name = version_name;
  }
}
