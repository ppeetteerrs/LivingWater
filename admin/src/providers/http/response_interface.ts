export interface searchResults {
  results: ResultItem[];
  time_taken: number;
}

export interface ResultItem {
  base_word_breakdowns: BaseWordBreakdown[];
  verse_location: string;
  verse_score: number;
  verse_text: {};
  parsed_text: {};
  ranking: number;
  expand: boolean;
  total_score: string;
  book_name: string;
  verse_book: string;
  book_index: number;
  start_chapter: string;
  start_verse: string;
  end_chapter: string;
  end_verse:string
}

interface BaseWordBreakdown {
  best_base_word: string;
  best_match_score: number;
  best_match_word: string;
  best_match_word_parent: string;
  breakdown: MatchWordBreakdown;
  rounded_score: string;
}

interface MatchWordBreakdown {
  db_id: number;
  decay: number;
  weight: number;
  parent: string;
  "relative popularity across verse": number;
  "relative popularity in verse": number;
  score: number;
  "term frequency": number;
  rounded_decay: string;
  rounded_weight: string;
  rounded_rpav: string;
  rounded_rpiv: string;
  rounded_score: string;
  rounded_tf: string;

}

export interface VerseRecord {
  location: string;
  new_location: string;
  text: {};
  parsed_text: {};
  max_vote: number;
  id: string;
  keywords: {word: string, level: number}[];
  l1: string[],
  l2: string[],
  l3: string[]
}
