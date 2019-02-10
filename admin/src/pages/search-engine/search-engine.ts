import { Component } from "@angular/core";
import {
  IonicPage,
  NavController,
  NavParams,
  ToastController
} from "ionic-angular";
import { Clipboard } from "@ionic-native/clipboard";
import { HttpProvider } from "../../providers/http/http";
import { ResultItem } from "../../providers/http/response_interface";
import { LoadingController } from "ionic-angular";
import { Observable } from "rxjs/Observable";
import { BibleBookListProvider } from "../../providers/bible-book-list/bible-book-list";

@IonicPage()
@Component({
  selector: "page-search-engine",
  templateUrl: "search-engine.html"
})
export class SearchEnginePage {
  input_sentence: string = "";
  results: ResultItem[] = null;
  time_taken: number = null;
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
    public navParams: NavParams,
    public toastCtrl: ToastController,
    public clipboard: Clipboard,
    public http: HttpProvider,
    public loadingCtrl: LoadingController,
    private bibleBooks: BibleBookListProvider
  ) {}

  async search(sentence) {
    this.results = null;
    this.time_taken = null;

    if (sentence == "") {
      this.presentToast("What do you expect from a blank line... zzzzzzzz");
      return false;
    }

    let loading;
    loading = this.loadingCtrl.create({
      content: "Please wait..."
    });

    loading.present();

    this.http
      .searchRankings(this.input_sentence)
      .do(response => {
        this.time_taken = response.time_taken;
      })
      .pluck("results")
      .map((results: ResultItem[]) => {
        let modified_results = results.map((item, index, arr) => {
          item.ranking = index + 1;
          item.expand = false;
          item.total_score = item.verse_score.toFixed(2);
          item.parsed_text = this.parseVerseText(item);
          item.book_name = item.verse_book;
          item.book_index = this.bibleBooks.getBookIndex(item.book_name);
          for (let breakdown_item of item.base_word_breakdowns) {
            //breakdown_item.breakdown = breakdown_item.breakdown;

            breakdown_item.rounded_score = breakdown_item.best_match_score.toFixed(
              2
            );
            if (breakdown_item.breakdown != null) {
              breakdown_item.breakdown.rounded_decay = breakdown_item.breakdown.decay.toFixed(
                2
              );
              breakdown_item.breakdown.rounded_weight = breakdown_item.breakdown.weight.toFixed(
                2
              );
              breakdown_item.breakdown.rounded_rpav = breakdown_item.breakdown[
                "relative popularity across verse"
              ].toFixed(2);
              breakdown_item.breakdown.rounded_rpiv = breakdown_item.breakdown[
                "relative popularity in verse"
              ].toFixed(2);
              breakdown_item.breakdown.rounded_score = breakdown_item.breakdown.score.toFixed(
                2
              );
              breakdown_item.breakdown.rounded_tf = breakdown_item.breakdown[
                "term frequency"
              ].toFixed(2);
            }
          }
          return item;
        });
        modified_results.sort((a, b) => {
          if (a.book_index < 0) {
            console.log(a.book_name);
          }
          if (b.book_index < 0) {
            console.log(b.book_name);
          }

          return b.verse_score - a.verse_score || a.book_index - b.book_index;
        });

        //Reorder rankings
        modified_results.map((item, index, arr) => {
          item.ranking = index + 1;
        });

        return modified_results;
      })
      .subscribe(
        results => {
          this.results = results;
          console.log(results);
        },
        err => {
          this.presentToast(err.error);
          loading.dismiss();
        },
        () => {
          loading.dismiss();
        }
      );
  }

  parseVerseText(item: ResultItem) {
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
    verse_text = verse_text.trim().replace(/ +/g, " ");

    let formatted_text = " " + verse_number + " " + verse_text;

    return formatted_text;
  }

  presentToast(message: string) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 7000
    });
    toast.present();
  }

  chooseVersion(version_name: string) {
    this.selected_version_name = version_name;
  }
}
