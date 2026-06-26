use clap::{Parser, Subcommand};
use serde::Serialize;
use serde_json::Value;
use toon_format::encode_default;

const BASE_URL: &str = "https://api.harvest-api.com/linkedin";

#[derive(Parser)]
#[command(name = "linkedin", about = "LinkedIn data CLI via HarvestAPI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Get a LinkedIn profile by URL or username
    Profile {
        /// LinkedIn profile URL or public identifier (username)
        target: String,
        /// Include email lookup
        #[arg(long)]
        email: bool,
    },
    /// Search LinkedIn profiles
    SearchProfiles {
        /// Search query (name, title, etc.)
        query: String,
        /// Filter by current company
        #[arg(long)]
        company: Option<String>,
        /// Filter by location
        #[arg(long)]
        location: Option<String>,
        /// Filter by job title
        #[arg(long)]
        title: Option<String>,
        /// Filter by school
        #[arg(long)]
        school: Option<String>,
        /// Filter by Geo ID
        #[arg(long)]
        geo_id: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get a company profile
    Company {
        /// Company URL, universal name, or search name
        target: String,
    },
    /// Search companies
    SearchCompanies {
        /// Search query
        query: String,
        /// Filter by company size: 1-10, 11-50, 51-200, etc.
        #[arg(long)]
        size: Option<String>,
        /// Filter by location
        #[arg(long)]
        location: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get posts from a profile
    Posts {
        /// Profile URL or username
        target: String,
        /// Time filter: 24h, week, month
        #[arg(long)]
        since: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get company posts
    CompanyPosts {
        /// Company URL or universal name
        target: String,
        /// Time filter: 24h, week, month
        #[arg(long)]
        since: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get a single post by URL
    Post {
        /// Post URL
        url: String,
    },
    /// Search posts by keyword
    SearchPosts {
        /// Search query
        query: String,
        /// Filter by author profile URL
        #[arg(long)]
        author: Option<String>,
        /// Filter by company
        #[arg(long)]
        company: Option<String>,
        /// Filter by group
        #[arg(long)]
        group: Option<String>,
        /// Time filter: 24h, week, month
        #[arg(long)]
        since: Option<String>,
        /// Sort by: relevance or date
        #[arg(long)]
        sort: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get comments on a post
    PostComments {
        /// Post URL
        url: String,
        /// Sort by: relevance or date
        #[arg(long)]
        sort: Option<String>,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get reactions on a post
    PostReactions {
        /// Post URL
        url: String,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get a job listing
    Job {
        /// Job URL or ID
        target: String,
    },
    /// Search job listings
    SearchJobs {
        /// Search query
        query: String,
        /// Location filter
        #[arg(long)]
        location: Option<String>,
        /// Geo ID for location filter
        #[arg(long)]
        geo_id: Option<String>,
        /// Time filter: 24h, week, month
        #[arg(long)]
        since: Option<String>,
        /// Workplace: office, hybrid, remote
        #[arg(long)]
        workplace: Option<String>,
        /// Employment: full-time, part-time, contract, internship
        #[arg(long)]
        employment: Option<String>,
        /// Salary: 40k+, 60k+, 80k+, 100k+, 120k+, 140k+, 160k+, 180k+, 200k+
        #[arg(long)]
        salary: Option<String>,
        /// Experience: internship, entry, associate, mid-senior, director, executive
        #[arg(long)]
        experience: Option<String>,
        /// Sort by: relevance or date
        #[arg(long)]
        sort: Option<String>,
        /// Easy Apply only
        #[arg(long)]
        easy_apply: bool,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get a LinkedIn group
    Group {
        /// Group URL or ID
        target: String,
    },
    /// Search groups
    SearchGroups {
        /// Search query
        query: String,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Search for a Geo ID by location name
    GeoId {
        /// Location name to search
        query: String,
    },
    /// Get comments on a profile's activity
    ProfileComments {
        /// Profile URL or username
        target: String,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
    /// Get reactions on a profile's activity
    ProfileReactions {
        /// Profile URL or username
        target: String,
        /// Page number
        #[arg(long, default_value = "1")]
        page: u32,
    },
}

// -- Cleaned output types --

#[derive(Serialize)]
struct Profile {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    username: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    headline: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    about: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    location: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    photo: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    connections: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    followers: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    premium: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    influencer: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    verified: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    open_to_work: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    hiring: Option<bool>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    experience: Vec<Experience>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    education: Vec<Education>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    skills: Vec<String>,
    #[serde(skip_serializing_if = "Vec::is_empty")]
    certifications: Vec<Certification>,
    #[serde(skip_serializing_if = "Option::is_none")]
    email: Option<String>,
}

#[derive(Serialize)]
struct Experience {
    #[serde(skip_serializing_if = "Option::is_none")]
    position: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    company: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    location: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    duration: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    start_date: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    end_date: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
}

#[derive(Serialize)]
struct Education {
    #[serde(skip_serializing_if = "Option::is_none")]
    school: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    degree: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    field: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    period: Option<String>,
}

#[derive(Serialize)]
struct Certification {
    #[serde(skip_serializing_if = "Option::is_none")]
    title: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    issued_by: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    issued_at: Option<String>,
}

#[derive(Serialize)]
struct ProfileSearchResult {
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    position: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    location: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    username: Option<String>,
}

#[derive(Serialize)]
struct Company {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    website: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    employee_count: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    followers: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    headquarter: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    logo: Option<String>,
}

#[derive(Serialize)]
struct Post {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    author: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    author_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posted_ago: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    likes: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    comments: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    shares: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    has_video: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    has_images: Option<bool>,
}

#[derive(Serialize)]
struct Job {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    title: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    state: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    company: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    company_url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    location: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posted_date: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    salary: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    employment_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    workplace_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    easy_apply: Option<bool>,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
}

#[derive(Serialize)]
struct JobSearchResult {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    title: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posted_date: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    company: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    location: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    easy_apply: Option<bool>,
}

#[derive(Serialize)]
struct Comment {
    #[serde(skip_serializing_if = "Option::is_none")]
    content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    author: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    posted_ago: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    likes: Option<u64>,
}

#[derive(Serialize)]
struct Reaction {
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    headline: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    reaction_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
}

#[derive(Serialize)]
struct Group {
    #[serde(skip_serializing_if = "Option::is_none")]
    id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    name: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    url: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    members: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    summary: Option<String>,
}

#[derive(Serialize)]
struct GeoId {
    #[serde(skip_serializing_if = "Option::is_none")]
    geo_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    title: Option<String>,
}

#[derive(Serialize)]
struct PaginatedResults<T: Serialize> {
    count: usize,
    #[serde(skip_serializing_if = "Option::is_none")]
    page: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    total_pages: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    total: Option<u64>,
    results: Vec<T>,
}

// -- API client --

fn get_api_key() -> String {
    std::env::var("HARVESTAPI_API_KEY").unwrap_or_else(|_| {
        eprintln!("error: HARVESTAPI_API_KEY not set");
        std::process::exit(1);
    })
}

fn api_get(endpoint: &str, params: &[(&str, &str)]) -> Result<Value, String> {
    let api_key = get_api_key();
    let url = format!("{BASE_URL}{endpoint}");

    let mut req = ureq::get(&url).header("X-API-Key", &api_key);
    for (k, v) in params {
        if !v.is_empty() {
            req = req.query(k, v);
        }
    }

    let mut resp = req.call().map_err(|e| format!("API error: {e}"))?;
    let body: Value = resp
        .body_mut()
        .read_json()
        .map_err(|e| format!("JSON parse error: {e}"))?;
    Ok(body)
}

fn toon_print<T: Serialize>(val: &T) {
    match encode_default(val) {
        Ok(s) => println!("{s}"),
        Err(e) => eprintln!("error: toon encode: {e}"),
    }
}

// -- Helpers --

fn is_url(s: &str) -> bool {
    s.starts_with("http://") || s.starts_with("https://") || s.starts_with("linkedin.com")
}

fn s(v: &Value, key: &str) -> Option<String> {
    v.get(key).and_then(|v| v.as_str()).map(|s| s.to_string())
}

fn u(v: &Value, key: &str) -> Option<u64> {
    v.get(key).and_then(|v| v.as_u64())
}

fn b(v: &Value, key: &str) -> Option<bool> {
    v.get(key).and_then(|v| v.as_bool())
}

fn nested_s(v: &Value, outer: &str, inner: &str) -> Option<String> {
    v.get(outer).and_then(|o| s(o, inner))
}

fn extract_pagination(data: &Value) -> (Option<u64>, Option<u64>, Option<u64>) {
    if let Some(p) = data.get("pagination") {
        (u(p, "pageNumber"), u(p, "totalPages"), u(p, "totalElements"))
    } else {
        (None, None, None)
    }
}

fn elements(data: &Value) -> Vec<&Value> {
    data.get("elements")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().collect())
        .unwrap_or_default()
}

fn element(data: &Value) -> &Value {
    data.get("element").unwrap_or(data)
}

// -- Data cleaners --

fn clean_profile(raw: &Value, include_email: bool) -> Profile {
    let experience = raw
        .get("experience")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .take(5)
                .map(|e| Experience {
                    position: s(e, "position"),
                    company: s(e, "companyName"),
                    location: s(e, "location"),
                    duration: s(e, "duration"),
                    start_date: nested_s(e, "startDate", "text"),
                    end_date: nested_s(e, "endDate", "text"),
                    description: s(e, "description"),
                })
                .collect()
        })
        .unwrap_or_default();

    let education = raw
        .get("education")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .take(5)
                .map(|e| {
                    let period = s(e, "period").or_else(|| {
                        let start = e.get("startDate").and_then(|d| u(d, "year"));
                        let end = e.get("endDate").and_then(|d| u(d, "year"));
                        match (start, end) {
                            (Some(s), Some(e)) => Some(format!("{s}-{e}")),
                            (Some(s), None) => Some(format!("{s}-")),
                            (None, Some(e)) => Some(format!("-{e}")),
                            _ => None,
                        }
                    });
                    Education {
                        school: s(e, "schoolName").or_else(|| s(e, "title")),
                        degree: s(e, "degree"),
                        field: s(e, "fieldOfStudy"),
                        period,
                    }
                })
                .collect()
        })
        .unwrap_or_default();

    let skills: Vec<String> = raw
        .get("skills")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().take(10).filter_map(|sk| s(sk, "name")).collect())
        .unwrap_or_default();

    let certifications = raw
        .get("certifications")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .take(5)
                .map(|c| Certification {
                    title: s(c, "title"),
                    issued_by: s(c, "issuedBy"),
                    issued_at: s(c, "issuedAt"),
                })
                .collect()
        })
        .unwrap_or_default();

    let first = s(raw, "firstName").unwrap_or_default();
    let last = s(raw, "lastName").unwrap_or_default();
    let name = format!("{first} {last}").trim().to_string();

    let photo = s(raw, "photo").or_else(|| nested_s(raw, "profilePicture", "url"));

    Profile {
        id: s(raw, "id"),
        username: s(raw, "publicIdentifier"),
        url: s(raw, "linkedinUrl"),
        name: if name.is_empty() { None } else { Some(name) },
        headline: s(raw, "headline"),
        about: s(raw, "about"),
        location: nested_s(raw, "location", "linkedinText"),
        photo,
        connections: u(raw, "connectionsCount"),
        followers: u(raw, "followerCount"),
        premium: b(raw, "premium"),
        influencer: b(raw, "influencer"),
        verified: b(raw, "verified"),
        open_to_work: b(raw, "openToWork"),
        hiring: b(raw, "hiring"),
        experience,
        education,
        skills,
        certifications,
        email: if include_email { s(raw, "email") } else { None },
    }
}

fn clean_profile_search(raw: &Value) -> ProfileSearchResult {
    ProfileSearchResult {
        name: s(raw, "name"),
        position: s(raw, "position"),
        location: nested_s(raw, "location", "linkedinText"),
        url: s(raw, "linkedinUrl"),
        username: s(raw, "publicIdentifier"),
    }
}

fn clean_company(raw: &Value) -> Company {
    let hq = raw
        .get("locations")
        .and_then(|v| v.as_array())
        .and_then(|arr| {
            arr.iter()
                .find(|l| b(l, "headquarter").unwrap_or(false))
                .or_else(|| arr.first())
        })
        .and_then(|l| nested_s(l, "parsed", "text").or_else(|| s(l, "city")));

    Company {
        id: s(raw, "id"),
        name: s(raw, "name"),
        url: s(raw, "linkedinUrl"),
        website: s(raw, "website"),
        description: s(raw, "description"),
        employee_count: u(raw, "employeeCount"),
        followers: u(raw, "followerCount"),
        headquarter: hq,
        logo: s(raw, "logo"),
    }
}

fn clean_post(raw: &Value) -> Post {
    Post {
        id: s(raw, "id"),
        url: s(raw, "linkedinUrl"),
        content: s(raw, "content"),
        author: nested_s(raw, "author", "name"),
        author_type: nested_s(raw, "author", "type"),
        posted_ago: raw.get("postedAt").and_then(|p| {
            s(p, "postedAgoText").or_else(|| s(p, "postedAgoShort"))
        }),
        likes: raw.get("engagement").and_then(|e| u(e, "likes")),
        comments: raw.get("engagement").and_then(|e| u(e, "comments")),
        shares: raw.get("engagement").and_then(|e| u(e, "shares")),
        has_video: Some(raw.get("postVideo").is_some()),
        has_images: raw
            .get("postImages")
            .and_then(|v| v.as_array())
            .map(|arr| !arr.is_empty()),
    }
}

fn clean_job(raw: &Value) -> Job {
    let salary = raw.get("salary").and_then(|sv| {
        s(sv, "text").or_else(|| {
            let min = sv.get("min").and_then(|v| v.as_f64());
            let max = sv.get("max").and_then(|v| v.as_f64());
            let currency = s(sv, "currency").unwrap_or_default();
            match (min, max) {
                (Some(mn), Some(mx)) => Some(format!("{mn:.0}-{mx:.0} {currency}")),
                _ => None,
            }
        })
    });

    Job {
        id: s(raw, "id"),
        title: s(raw, "title"),
        url: s(raw, "linkedinUrl").or_else(|| s(raw, "url")),
        state: s(raw, "jobState"),
        company: nested_s(raw, "company", "name").or_else(|| s(raw, "companyName")),
        company_url: nested_s(raw, "company", "linkedinUrl").or_else(|| s(raw, "companyLink")),
        location: nested_s(raw, "location", "linkedinText"),
        posted_date: s(raw, "postedDate"),
        salary,
        employment_type: s(raw, "employmentType"),
        workplace_type: s(raw, "workplaceType"),
        easy_apply: b(raw, "easyApply"),
        description: s(raw, "descriptionText"),
    }
}

fn clean_job_search(raw: &Value) -> JobSearchResult {
    JobSearchResult {
        id: s(raw, "id"),
        title: s(raw, "title"),
        url: s(raw, "url"),
        posted_date: s(raw, "postedDate"),
        company: nested_s(raw, "company", "name"),
        location: nested_s(raw, "location", "linkedinText"),
        easy_apply: b(raw, "easyApply"),
    }
}

fn clean_comment(raw: &Value) -> Comment {
    Comment {
        content: s(raw, "content"),
        author: nested_s(raw, "author", "name"),
        posted_ago: nested_s(raw, "postedAt", "postedAgoText"),
        likes: raw.get("engagement").and_then(|e| u(e, "likes")),
    }
}

fn clean_reaction(raw: &Value) -> Reaction {
    Reaction {
        name: s(raw, "name"),
        headline: s(raw, "headline"),
        reaction_type: s(raw, "reactionType"),
        url: s(raw, "linkedinUrl"),
    }
}

fn clean_group(raw: &Value) -> Group {
    Group {
        id: s(raw, "id"),
        name: s(raw, "name"),
        url: s(raw, "linkedinUrl"),
        members: u(raw, "members").or_else(|| u(raw, "memberCount")),
        summary: s(raw, "summary").or_else(|| s(raw, "description")),
    }
}

fn clean_geo_id(raw: &Value) -> GeoId {
    GeoId {
        geo_id: s(raw, "geoId"),
        title: s(raw, "title"),
    }
}

// -- Paginated output helper --

fn print_paginated<T: Serialize, F>(data: &Value, cleaner: F)
where
    F: Fn(&Value) -> T,
{
    let items = elements(data);
    let results: Vec<T> = items.iter().map(|v| cleaner(v)).collect();
    let (page, total_pages, total) = extract_pagination(data);
    toon_print(&PaginatedResults {
        count: results.len(),
        page,
        total_pages,
        total,
        results,
    });
}

// -- Command handlers --

fn cmd_profile(target: &str, email: bool) {
    let mut params: Vec<(&str, &str)> = Vec::new();
    if is_url(target) {
        params.push(("url", target));
    } else {
        params.push(("publicIdentifier", target));
    }
    if email {
        params.push(("findEmail", "true"));
    }

    match api_get("/profile", &params) {
        Ok(data) => toon_print(&clean_profile(element(&data), email)),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_search_profiles(
    query: &str,
    company: &Option<String>,
    location: &Option<String>,
    title: &Option<String>,
    school: &Option<String>,
    geo_id: &Option<String>,
    page: u32,
) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("search", query), ("page", &page_str)];
    if let Some(c) = company { params.push(("currentCompany", c)); }
    if let Some(l) = location { params.push(("location", l)); }
    if let Some(t) = title { params.push(("title", t)); }
    if let Some(s) = school { params.push(("school", s)); }
    if let Some(g) = geo_id { params.push(("geoId", g)); }

    match api_get("/profile-search", &params) {
        Ok(data) => print_paginated(&data, clean_profile_search),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_company(target: &str) {
    let mut params: Vec<(&str, &str)> = Vec::new();
    if is_url(target) {
        params.push(("url", target));
    } else {
        params.push(("universalName", target));
    }

    match api_get("/company", &params) {
        Ok(data) => toon_print(&clean_company(element(&data))),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_search_companies(query: &str, size: &Option<String>, location: &Option<String>, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("search", query), ("page", &page_str)];
    if let Some(s) = size { params.push(("companySize", s)); }
    if let Some(l) = location { params.push(("location", l)); }

    match api_get("/company-search", &params) {
        Ok(data) => print_paginated(&data, clean_company),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_posts(target: &str, since: &Option<String>, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("page", &page_str)];
    if is_url(target) {
        params.push(("profile", target));
    } else {
        params.push(("profilePublicIdentifier", target));
    }
    if let Some(s) = since { params.push(("postedLimit", s)); }

    match api_get("/profile-posts", &params) {
        Ok(data) => print_paginated(&data, clean_post),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_company_posts(target: &str, since: &Option<String>, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("page", &page_str)];
    if is_url(target) {
        params.push(("company", target));
    } else {
        params.push(("companyUniversalName", target));
    }
    if let Some(s) = since { params.push(("postedLimit", s)); }

    match api_get("/company-posts", &params) {
        Ok(data) => print_paginated(&data, clean_post),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_post(url: &str) {
    match api_get("/post", &[("url", url)]) {
        Ok(data) => toon_print(&clean_post(element(&data))),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_search_posts(
    query: &str,
    author: &Option<String>,
    company: &Option<String>,
    group: &Option<String>,
    since: &Option<String>,
    sort: &Option<String>,
    page: u32,
) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("search", query), ("page", &page_str)];
    if let Some(a) = author { params.push(("profile", a)); }
    if let Some(c) = company { params.push(("company", c)); }
    if let Some(g) = group { params.push(("group", g)); }
    if let Some(s) = since { params.push(("postedLimit", s)); }
    if let Some(s) = sort { params.push(("sortBy", s)); }

    match api_get("/post-search", &params) {
        Ok(data) => print_paginated(&data, clean_post),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_post_comments(url: &str, sort: &Option<String>, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("post", url), ("page", &page_str)];
    if let Some(s) = sort { params.push(("sortBy", s)); }

    match api_get("/post-comments", &params) {
        Ok(data) => print_paginated(&data, clean_comment),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_post_reactions(url: &str, page: u32) {
    let page_str = page.to_string();
    let params = [("post", url), ("page", &page_str)];

    match api_get("/post-reactions", &params) {
        Ok(data) => print_paginated(&data, clean_reaction),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_job(target: &str) {
    let mut params: Vec<(&str, &str)> = Vec::new();
    if is_url(target) {
        params.push(("url", target));
    } else {
        params.push(("jobId", target));
    }

    match api_get("/job", &params) {
        Ok(data) => toon_print(&clean_job(element(&data))),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_search_jobs(
    query: &str,
    location: &Option<String>,
    geo_id: &Option<String>,
    since: &Option<String>,
    workplace: &Option<String>,
    employment: &Option<String>,
    salary: &Option<String>,
    experience: &Option<String>,
    sort: &Option<String>,
    easy_apply: bool,
    page: u32,
) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("search", query), ("page", &page_str)];
    if let Some(l) = location { params.push(("location", l)); }
    if let Some(g) = geo_id { params.push(("geoId", g)); }
    if let Some(s) = since { params.push(("postedLimit", s)); }
    if let Some(w) = workplace { params.push(("workplaceType", w)); }
    if let Some(e) = employment { params.push(("employmentType", e)); }
    if let Some(s) = salary { params.push(("salary", s)); }
    if let Some(e) = experience { params.push(("experienceLevel", e)); }
    if let Some(s) = sort { params.push(("sortBy", s)); }
    if easy_apply { params.push(("easyApply", "true")); }

    match api_get("/job-search", &params) {
        Ok(data) => print_paginated(&data, clean_job_search),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_group(target: &str) {
    let mut params: Vec<(&str, &str)> = Vec::new();
    if is_url(target) {
        params.push(("url", target));
    } else {
        params.push(("groupId", target));
    }

    match api_get("/group", &params) {
        Ok(data) => toon_print(&clean_group(element(&data))),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_search_groups(query: &str, page: u32) {
    let page_str = page.to_string();
    let params = [("search", query), ("page", &page_str)];

    match api_get("/group-search", &params) {
        Ok(data) => print_paginated(&data, clean_group),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_geo_id(query: &str) {
    match api_get("/geo-id-search", &[("search", query)]) {
        Ok(data) => print_paginated(&data, clean_geo_id),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_profile_comments(target: &str, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("page", &page_str)];
    if is_url(target) {
        params.push(("profile", target));
    } else {
        params.push(("profilePublicIdentifier", target));
    }

    match api_get("/profile-comments", &params) {
        Ok(data) => print_paginated(&data, clean_comment),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn cmd_profile_reactions(target: &str, page: u32) {
    let page_str = page.to_string();
    let mut params: Vec<(&str, &str)> = vec![("page", &page_str)];
    if is_url(target) {
        params.push(("profile", target));
    } else {
        params.push(("profilePublicIdentifier", target));
    }

    match api_get("/profile-reactions", &params) {
        Ok(data) => print_paginated(&data, clean_reaction),
        Err(e) => eprintln!("error: {e}"),
    }
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Commands::Profile { ref target, email } => cmd_profile(target, email),
        Commands::SearchProfiles { ref query, ref company, ref location, ref title, ref school, ref geo_id, page } =>
            cmd_search_profiles(query, company, location, title, school, geo_id, page),
        Commands::Company { ref target } => cmd_company(target),
        Commands::SearchCompanies { ref query, ref size, ref location, page } =>
            cmd_search_companies(query, size, location, page),
        Commands::Posts { ref target, ref since, page } => cmd_posts(target, since, page),
        Commands::CompanyPosts { ref target, ref since, page } => cmd_company_posts(target, since, page),
        Commands::Post { ref url } => cmd_post(url),
        Commands::SearchPosts { ref query, ref author, ref company, ref group, ref since, ref sort, page } =>
            cmd_search_posts(query, author, company, group, since, sort, page),
        Commands::PostComments { ref url, ref sort, page } => cmd_post_comments(url, sort, page),
        Commands::PostReactions { ref url, page } => cmd_post_reactions(url, page),
        Commands::Job { ref target } => cmd_job(target),
        Commands::SearchJobs { ref query, ref location, ref geo_id, ref since, ref workplace, ref employment, ref salary, ref experience, ref sort, easy_apply, page } =>
            cmd_search_jobs(query, location, geo_id, since, workplace, employment, salary, experience, sort, easy_apply, page),
        Commands::Group { ref target } => cmd_group(target),
        Commands::SearchGroups { ref query, page } => cmd_search_groups(query, page),
        Commands::GeoId { ref query } => cmd_geo_id(query),
        Commands::ProfileComments { ref target, page } => cmd_profile_comments(target, page),
        Commands::ProfileReactions { ref target, page } => cmd_profile_reactions(target, page),
    }
}
