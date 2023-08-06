from src import constants, data_framing, data_scraping, gcs
import pendulum

key = constants.AUTH_DATA
project_id = constants.PROJECT_ID
bucket_name = constants.BUCKET_NAME
temp_file_path = "webapp_aisekiya/temp/temp.parquet"
blob_name = f"data_{pendulum.now('UTC').in_timezone('Asia/Tokyo').strftime('%Y_%m_%d_%H_%M')}.parquet"
blob_directory = f"aisekiya_congestion/"



def main() -> None:
    url = "https://aiseki-ya.com/"
    get_stores = data_scraping.GetStores(url)
    get_stores.get_stores()

    get_store_data = data_scraping.GetStoreData(get_stores.stores)
    get_store_data.iterable()

    data_framing.generating_df(get_store_data.all_store_data)

    gcs_upload = gcs.GCSBucket(
        project_id=project_id,
        bucket_name=bucket_name,
        blob_name=blob_name,
        blob_directory=blob_directory,
    )
    gcs_upload.create_client(key=key)
    gcs_upload.uploading()


if __name__ == "__main__":
    main()
