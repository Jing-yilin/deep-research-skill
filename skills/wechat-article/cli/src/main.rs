use clap::{Parser, Subcommand};
use regex::Regex;
use reqwest::blocking::Client;
use serde::Serialize;
use serde_json::Value;
use std::env;
use std::fs;
use std::process;
use toon_format::encode_default;

#[derive(Parser)]
#[command(name = "wxa", about = "WeChat Article CLI with TOON output")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Search WeChat Official Accounts
    Search {
        keyword: String,
        #[arg(short, long, default_value = "5")]
        limit: u32,
    },
    /// List articles from an account
    List {
        fakeid: String,
        #[arg(short, long, default_value = "10")]
        limit: u32,
    },
    /// Download article content
    Download {
        url: String,
        #[arg(short, long, default_value = "markdown")]
        format: String,
        #[arg(short, long)]
        output: Option<String>,
    },
    /// Find source account from article URL
    Source {
        url: String,
    },
}

#[derive(Serialize)]
struct SearchResult {
    query: String,
    total: u64,
    accounts: Vec<Account>,
}

#[derive(Serialize)]
struct Account {
    fakeid: String,
    name: String,
    alias: String,
    bio: String,
}

#[derive(Serialize)]
struct ArticleListResult {
    fakeid: String,
    count: usize,
    articles: Vec<Article>,
}

#[derive(Serialize)]
struct Article {
    title: String,
    date: String,
    author: String,
    url: String,
}

fn get_config() -> (String, String) {
    let base_url = env::var("WECHAT_API_BASE_URL").unwrap_or_default();
    let api_key = env::var("WECHAT_API_KEY").unwrap_or_default();
    if base_url.is_empty() {
        eprintln!("error: WECHAT_API_BASE_URL not set");
        process::exit(1);
    }
    (base_url, api_key)
}

fn check_api_error(json: &Value) -> Option<String> {
    let ret = json.get("base_resp")?.get("ret")?.as_i64()?;
    if ret != 0 {
        let msg = json["base_resp"]["err_msg"].as_str().unwrap_or("unknown error");
        return Some(msg.to_string());
    }
    None
}

fn format_timestamp(ts: i64) -> String {
    if ts == 0 {
        return String::new();
    }
    let secs = ts;
    let days_since_epoch = secs / 86400;
    let mut y = 1970i64;
    let mut remaining = days_since_epoch;

    loop {
        let days_in_year = if y % 4 == 0 && (y % 100 != 0 || y % 400 == 0) { 366 } else { 365 };
        if remaining < days_in_year {
            break;
        }
        remaining -= days_in_year;
        y += 1;
    }

    let leap = y % 4 == 0 && (y % 100 != 0 || y % 400 == 0);
    let month_days = [
        31,
        if leap { 29 } else { 28 },
        31, 30, 31, 30, 31, 31, 30, 31, 30, 31,
    ];
    let mut m = 0usize;
    for (i, &d) in month_days.iter().enumerate() {
        if remaining < d as i64 {
            m = i;
            break;
        }
        remaining -= d as i64;
    }

    format!("{:04}-{:02}-{:02}", y, m + 1, remaining + 1)
}

fn clean_markdown(content: &str) -> String {
    // Remove CSS prefix: find first heading (#) or image (![) marker
    let s = if let Some(pos) = content.find('#').or_else(|| content.find("![")) {
        &content[pos..]
    } else {
        content
    };
    let mut s = s.to_string();

    let re_inline_css = Regex::new(r"(?s)#js_row_immersive[^}]*\}").unwrap();
    let re_sns = Regex::new(r"(?s)\.sns_opr_btn[^}]*\}").unwrap();
    let re_img_css = Regex::new(r"img\s*\{[^}]*\}").unwrap();
    let re_thumb = Regex::new(r"(?s)THUMB\s*\n*STOPPING\s*\n*").unwrap();
    let re_js_void = Regex::new(r"\[([^\]]+)\]\(javascript:void\\\(0\\\);\)").unwrap();
    let re_reader = Regex::new(r"(?s)在小说阅读器中沉浸阅读\s*\n*").unwrap();

    s = re_inline_css.replace_all(&s, "").to_string();
    s = re_sns.replace_all(&s, "").to_string();
    s = re_img_css.replace_all(&s, "").to_string();
    s = re_thumb.replace_all(&s, "").to_string();
    s = re_js_void.replace_all(&s, "$1").to_string();
    s = re_reader.replace_all(&s, "").to_string();

    let mut lines: Vec<String> = Vec::new();
    let mut started = false;
    let mut prev_blank = false;

    for line in s.lines() {
        let stripped = line.trim();
        if stripped.starts_with("#js_") || stripped.starts_with("img {") {
            continue;
        }
        if stripped.contains("max-width") && stripped.contains('{') {
            continue;
        }
        if !started && stripped.is_empty() {
            continue;
        }
        started = true;
        let is_blank = stripped.is_empty();
        if is_blank && prev_blank {
            continue;
        }
        prev_blank = is_blank;
        lines.push(line.trim_end().to_string());
    }

    lines.join("\n").trim().to_string()
}

fn cmd_search(keyword: &str, limit: u32) {
    let (base_url, api_key) = get_config();
    let client = Client::new();

    let resp = client
        .get(format!("{}/api/public/v1/account", base_url))
        .query(&[("keyword", keyword), ("size", &limit.to_string())])
        .header("X-Auth-Key", &api_key)
        .send();

    let json: Value = match resp {
        Ok(r) => r.json().unwrap_or_else(|e| {
            eprintln!("error: failed to parse response: {e}");
            process::exit(1);
        }),
        Err(e) => {
            eprintln!("error: request failed: {e}");
            process::exit(1);
        }
    };

    if let Some(err) = check_api_error(&json) {
        eprintln!("error: {err}");
        process::exit(1);
    }

    let list = json["list"].as_array().cloned().unwrap_or_default();
    let total = json["total"].as_u64().unwrap_or(0);

    let accounts: Vec<Account> = list
        .iter()
        .map(|a| Account {
            fakeid: a["fakeid"].as_str().unwrap_or("").to_string(),
            name: a["nickname"].as_str().unwrap_or("").to_string(),
            alias: a["alias"].as_str().unwrap_or("").to_string(),
            bio: a["signature"].as_str().unwrap_or("").to_string(),
        })
        .collect();

    let result = SearchResult {
        query: keyword.to_string(),
        total,
        accounts,
    };

    match encode_default(&result) {
        Ok(toon) => println!("{toon}"),
        Err(e) => eprintln!("error: toon encode failed: {e}"),
    }
}

fn cmd_list(fakeid: &str, limit: u32) {
    let (base_url, api_key) = get_config();
    let client = Client::new();

    let resp = client
        .get(format!("{}/api/public/v1/article", base_url))
        .query(&[("fakeid", fakeid), ("size", &limit.to_string())])
        .header("X-Auth-Key", &api_key)
        .send();

    let json: Value = match resp {
        Ok(r) => r.json().unwrap_or_else(|e| {
            eprintln!("error: failed to parse response: {e}");
            process::exit(1);
        }),
        Err(e) => {
            eprintln!("error: request failed: {e}");
            process::exit(1);
        }
    };

    if let Some(err) = check_api_error(&json) {
        eprintln!("error: {err}");
        process::exit(1);
    }

    let articles_raw = json["articles"].as_array().cloned().unwrap_or_default();

    let articles: Vec<Article> = articles_raw
        .iter()
        .map(|a| Article {
            title: a["title"].as_str().unwrap_or("").to_string(),
            date: format_timestamp(a["update_time"].as_i64().unwrap_or(0)),
            author: a["author_name"].as_str().unwrap_or("").to_string(),
            url: a["link"].as_str().unwrap_or("").to_string(),
        })
        .collect();

    let count = articles.len();
    let result = ArticleListResult {
        fakeid: fakeid.to_string(),
        count,
        articles,
    };

    match encode_default(&result) {
        Ok(toon) => println!("{toon}"),
        Err(e) => eprintln!("error: toon encode failed: {e}"),
    }
}

fn cmd_download(url: &str, format: &str, output: Option<&str>) {
    let (base_url, _) = get_config();
    let client = Client::builder()
        .timeout(std::time::Duration::from_secs(30))
        .build()
        .unwrap();

    let resp = client
        .get(format!("{}/api/public/v1/download", base_url))
        .query(&[("url", url), ("format", format)])
        .send();

    let content = match resp {
        Ok(r) => {
            let status = r.status();
            let body = r.text().unwrap_or_else(|e| {
                eprintln!("error: failed to read response: {e}");
                process::exit(1);
            });
            if !status.is_success() {
                eprintln!("error: server returned {status}");
                eprintln!("{body}");
                process::exit(1);
            }
            body
        }
        Err(e) => {
            eprintln!("error: request failed: {e}");
            process::exit(1);
        }
    };

    let cleaned = if format == "markdown" {
        clean_markdown(&content)
    } else {
        content
    };

    if let Some(path) = output {
        fs::write(path, &cleaned).unwrap_or_else(|e| {
            eprintln!("error: failed to write file: {e}");
            process::exit(1);
        });
        println!("saved: {path}");
    } else {
        println!("{cleaned}");
    }
}

fn cmd_source(url: &str) {
    let (base_url, api_key) = get_config();
    let client = Client::new();

    let resp = client
        .get(format!("{}/api/public/v1/accountbyurl", base_url))
        .query(&[("url", url)])
        .header("X-Auth-Key", &api_key)
        .send();

    let json: Value = match resp {
        Ok(r) => r.json().unwrap_or_else(|e| {
            eprintln!("error: failed to parse response: {e}");
            process::exit(1);
        }),
        Err(e) => {
            eprintln!("error: request failed: {e}");
            process::exit(1);
        }
    };

    if let Some(err) = check_api_error(&json) {
        eprintln!("error: {err}");
        process::exit(1);
    }

    let list = json["list"].as_array().cloned().unwrap_or_default();
    let total = json["total"].as_u64().unwrap_or(0);

    let accounts: Vec<Account> = list
        .iter()
        .map(|a| Account {
            fakeid: a["fakeid"].as_str().unwrap_or("").to_string(),
            name: a["nickname"].as_str().unwrap_or("").to_string(),
            alias: a["alias"].as_str().unwrap_or("").to_string(),
            bio: a["signature"].as_str().unwrap_or("").to_string(),
        })
        .collect();

    let result = SearchResult {
        query: url.to_string(),
        total,
        accounts,
    };

    match encode_default(&result) {
        Ok(toon) => println!("{toon}"),
        Err(e) => eprintln!("error: toon encode failed: {e}"),
    }
}

fn main() {
    let cli = Cli::parse();
    match &cli.command {
        Commands::Search { keyword, limit } => cmd_search(keyword, *limit),
        Commands::List { fakeid, limit } => cmd_list(fakeid, *limit),
        Commands::Download { url, format, output } => {
            cmd_download(url, format, output.as_deref())
        }
        Commands::Source { url } => cmd_source(url),
    }
}
