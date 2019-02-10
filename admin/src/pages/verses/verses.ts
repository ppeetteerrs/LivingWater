import { Component } from "@angular/core";
import {
  IonicPage,
  NavController,
  NavParams,
  ToastController,
  AlertController,
  ModalController,
  LoadingController,
  ViewController
} from "ionic-angular";
import { HttpProvider } from "../../providers/http/http";
import { Observable } from "rxjs/Observable";
import { VerseRecord, ResultItem } from "../../providers/http/response_interface";
import { AddVersePage } from "../add-verse/add-verse";

@IonicPage()
@Component({
  selector: "page-verses",
  templateUrl: "verses.html"
})
export class VersesPage {
  search_input: string = "";
  verse_record: VerseRecord = null;
  bible_versions: any[] = [{
    display_title: "NIV",
    version_name: "niv"
  }, {
    display_title: "和合本",
    version_name: "cuv"
  }];

  selected_version_name: string = "niv";

  constructor(
    public navCtrl: NavController,
    public navParams: NavParams,
    public toastCtrl: ToastController,
    public http: HttpProvider,
    public loadingCtrl: LoadingController,
    public alertCtrl: AlertController,
    public modalCtrl: ModalController
  ) {}

  async searchVerse(search_input, load: boolean = true, loader = null) {
    if (search_input == "") {
      this.presentToast(
        "The result of searching for a blank line is @#$!@%^!$^&!&!!#%!"
      );
      return false;
    }
    let loading;
    if (load) {
      loading = this.loadingCtrl.create({
        content: "Please wait..."
      });
      loading.present();
    }

    console.log("Searching for: " + search_input);

    this.http
      .searchVerse(search_input)
      .do(record => {
        console.log(record);
        record.parsed_text = this.parseVerseText(record);
        record.l1 = record.keywords
          .filter((item, index, arr) => {
            return item.level == 1;
          })
          .map((item, index, arr) => {
            return item.word;
          });
        record.l2 = record.keywords
          .filter((item, index, arr) => {
            return item.level == 2;
          })
          .map((item, index, arr) => {
            return item.word;
          });
        record.l3 = record.keywords
          .filter((item, index, arr) => {
            return item.level == 3;
          })
          .map((item, index, arr) => {
            return item.word;
          });
        console.log(record);
        return record;
      })
      .subscribe(
        record => {
          this.search_input = "";
          this.verse_record = record;
          console.log(this.verse_record);
        },
        err => {
          this.search_input = "";
          this.presentToast(err.error);
          if (load) {
            loading.dismiss();
          } else if (loader != null) {
            loader.dismiss();
          }
        },
        () => {
          if (load) {
            loading.dismiss();
          } else if (loader != null) {
            loader.dismiss();
          }
        }
      );
  }

  presentToast(message: string) {
    let toast = this.toastCtrl.create({
      message: message,
      duration: 7000
    });
    toast.present();
  }

  addKeyword(level: number) {
    this.showAddKeywordPrompt(level);
  }

  editKeyword(keyword: string, level: number) {
    this.showEditKeywordPrompt(keyword, level);
  }

  showDeleteKeywordPrompt(keyword: string, level: number) {
    const alert = this.alertCtrl.create({
      title:
        "Do you want to delete the word " +
        keyword +
        " from " +
        this.verse_record.location,
      buttons: [
        {
          text: "Cancel",
          role: "cancel",
          handler: data => {}
        },
        {
          text: "Confirm",
          handler: data => {
            this.deleteKeyword(keyword, level);
          }
        }
      ]
    });
    alert.present();
  }

  deleteKeyword(keyword: string, level: number) {
    this.sendEditLinkRequest(this.verse_record.location, keyword, level, true);
  }

  showAddKeywordPrompt(level: number) {
    let prompt = this.alertCtrl.create({
      title: "Add a Level " + level + " Keyword",
      message: "Enter a keyword to be added",
      inputs: [
        {
          name: "keyword",
          placeholder: "Keyword"
        }
      ],
      buttons: [
        {
          text: "Cancel"
        },
        {
          text: "Confirm",
          handler: data => {
            console.log(level + 1);
            this.sendEditLinkRequest(
              this.verse_record.location,
              data.keyword,
              level,
              false
            );
          }
        }
      ]
    });
    prompt.present();
  }

  showEditKeywordPrompt(keyword: string, level: number) {
    let alert = this.alertCtrl.create({
      title: "Choose a level for keyword " + keyword
    });

    alert.addInput({
      type: "radio",
      label: "1",
      value: "1",
      checked: level == 1
    });

    alert.addInput({
      type: "radio",
      label: "2",
      value: "2",
      checked: level == 2
    });

    alert.addInput({
      type: "radio",
      label: "3",
      value: "3",
      checked: level == 3
    });

    alert.addButton("Cancel");
    alert.addButton({
      text: "OK",
      handler: data => {
        console.log(data + 1);
        this.sendEditLinkRequest(
          this.verse_record.location,
          keyword,
          parseInt(data),
          false
        );
      }
    });
    alert.present();
  }

  sendEditLinkRequest(
    location: string,
    word: string,
    level: number,
    delete_item: boolean
  ) {
    let loading;
    loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    loading.present();
    this.http.editKeywordLink(location, word, level, delete_item).subscribe(
      response => {
        console.log("Location: " + location);
        console.log("Response: " + response);
        this.searchVerse(location, false, loading);
      },
      err => {
        this.presentToast(err.error);
        loading.dismiss();
      }
    );
  }

  showEditLocationPrompt(location: string) {
    let prompt = this.alertCtrl.create({
      title: "Editing Verse Location",
      message: "Change from " + location + " to:",
      inputs: [
        {
          name: "new_location",
          placeholder: "New Location"
        }
      ],
      buttons: [
        {
          text: "Cancel"
        },
        {
          text: "Confirm",
          handler: data => {
            console.log(data.new_location + 1);
            this.sendEditLocationRequest(location, data.new_location);
          }
        }
      ]
    });
    prompt.present();
  }

  sendEditLocationRequest(old_location: string, new_location: string) {
    let loading;
    loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    this.http.editVerseLocation(old_location, new_location).subscribe(
      response => {
        console.log(response);
        this.searchVerse(new_location, false, loading);
      },
      err => {
        this.presentToast(err.error);
        loading.dismiss();
      }
    );
  }

  addVerse() {
    let addVerseModal = this.modalCtrl.create("AddVersePage", {
      userId: 8675309
    });
    addVerseModal.onDidDismiss(httpObservable => {
      if (httpObservable != null) {
        let loading;
        loading = this.loadingCtrl.create({
          content: "Please wait..."
        });
        httpObservable.subscribe(
          response => {
            this.searchVerse(response.location, false, loading);
          },
          err => {
            this.presentToast(err.error);
            loading.dismiss();
          }
        );
      }
    });
    addVerseModal.present();
  }

  removeVersePrompt() {
    if (this.verse_record != null) {
      let prompt = this.alertCtrl.create({
        title:
          "Are you sure to want to remove verse " +
          this.verse_record.location +
          "?",
        buttons: [
          {
            text: "Cancel"
          },
          {
            text: "Confirm",
            handler: data => {
              this.removeVerse();
            }
          }
        ]
      });
      prompt.present();
    } else {
      this.presentToast("Dont Play with the buttons!");
    }
  }

  removeVerse() {
    let loading;
    loading = this.loadingCtrl.create({
      content: "Please wait..."
    });
    this.http.removeVerse(this.verse_record.location).subscribe(
      response => {
        this.verse_record = null;
        this.search_input = "";
        this.presentToast("Remove Verse " + response.location);
        loading.dismiss();
      },
      err => {
        this.presentToast(err.error);
        loading.dismiss();
      }
    );
  }

  parseVerseText(item: any) {
    // Create response object
    let response = {};
    let verse_text = item.text;
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
  chooseVersion(version_name: string) {
    this.selected_version_name = version_name;
  }
}
