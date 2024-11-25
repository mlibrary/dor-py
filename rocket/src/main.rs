#[macro_use] extern crate rocket;

#[cfg(test)]
mod tests;
mod paste_id;

use std::io;

use tokio::runtime::Runtime;

use rocket::data::{Data, ToByteUnit};
use rocket::http::uri::Absolute;
use rocket::response::content::RawText;
use rocket::tokio::fs::{self, File};

use paste_id::PasteId;

// In a real application, these would be retrieved dynamically from a config.
const HOST: Absolute<'static> = uri!("http://localhost:8000");
const ID_LENGTH: usize = 3;

use std::sync::LazyLock;
use std::env;
static DATABASE_URL: LazyLock<String> = LazyLock::new(|| {
    env::var("DATABASE_URL").unwrap()
});

#[derive(Debug, sqlx::FromRow)]
struct Ticket {
    id: String,
}

async fn init_database() -> () {
    let pool = sqlx::sqlite::SqlitePool::connect(&*DATABASE_URL).await.unwrap();
    sqlx::migrate!().run(&pool).await.unwrap();
}

#[post("/", data = "<paste>")]
async fn upload(paste: Data<'_>) -> io::Result<String> {
    let id = PasteId::new(ID_LENGTH);
    let pool = sqlx::sqlite::SqlitePool::connect(&*DATABASE_URL).await.unwrap();
    let value = id.value();
    sqlx::query!("INSERT INTO tickets (id) VALUES ($1)", value).execute(&pool).await.unwrap();
    paste.open(128.kibibytes()).into_file(id.file_path()).await?;
    Ok(uri!(HOST, retrieve(id)).to_string())
}

#[get("/<id>")]
async fn retrieve(id: PasteId<'_>) -> Option<RawText<File>> {
    File::open(id.file_path()).await.map(RawText).ok()
}

#[delete("/<id>")]
async fn delete(id: PasteId<'_>) -> Option<()> {
    fs::remove_file(id.file_path()).await.ok()
}

#[get("/")]
fn index() -> &'static str {
    "
    USAGE

      POST /

          accepts zipped submission package data in the body of the request and
          responds with a URL of a page containing the submission's status

          EXAMPLE: curl --data-binary @submission.zip http://localhost:8000

      GET /<id>

          retrieves the status of the submission with id `<id>`
    "
}

#[launch]
fn rocket() -> _ {
    println!("Starting Rocket...");
    println!("DATABASE_URL: {}", &*DATABASE_URL);
    // let rt = Runtime::new().unwrap();
    // let init_db = init_database();
    // rt.block_on(init_db);
    rocket::build().mount("/", routes![index, upload, delete, retrieve])
}
