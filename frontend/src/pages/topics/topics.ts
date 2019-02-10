import {Component} from '@angular/core';
import {IonicPage, NavController, NavParams} from 'ionic-angular';
import {LocalVersesProvider} from '../../providers/local-verses/local-verses';

@IonicPage()
@Component({
  selector: 'page-topics',
  templateUrl: 'topics.html'
})
export class TopicsPage {
  topics;
  display_topics;
  searchInput: string;

  constructor(
    public navCtrl: NavController,
    public navParams: NavParams,
    public verses: LocalVersesProvider
  ) {
    this.topics = Object.keys(verses.topics_data);
    this.display_topics = this.topics;
  }

  localSearch() {
    this.display_topics = this.verses.localSearch(
      this.searchInput,
      this.topics
    );
  }

  openTopic(topic: string) {
    this.navCtrl.push('VerseListPage', {
      title: topic,
      data: this.verses.topics_data[topic]
    });
  }
}
