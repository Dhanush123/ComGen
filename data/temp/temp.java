package com.x10host.dhanushpatel.phototagger;

import android.Manifest;
import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.SearchManager;
import android.content.ContentResolver;
import android.content.ContentUris;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.drawable.BitmapDrawable;
import android.media.ThumbnailUtils;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.preference.PreferenceManager;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.provider.Settings;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.text.InputType;
import android.text.method.ScrollingMovementMethod;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.RelativeLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.clarifai.api.ClarifaiClient;
import com.clarifai.api.RecognitionRequest;
import com.clarifai.api.RecognitionResult;
import com.clarifai.api.Tag;
import com.google.android.gms.appindexing.Action;
import com.google.android.gms.appindexing.AppIndex;
import com.google.android.gms.common.api.GoogleApiClient;
import com.x10host.dhanushpatel.phototagger.alchemy_api.AlchemyAPI;
import com.x10host.dhanushpatel.phototagger.alchemy_api.AlchemyAPI_ImageParams;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;
import java.util.List;

public class MainActivity extends AppCompatActivity {

  private static final int TAKE_PICTURE = 1;
  private static final int PICK_PHOTO = 2;
  private static final int PICK_VIDEO = 3;
  private static final int MULT_PERMISSIONS = 100;

  String[] permissions = new String[] { Manifest.permission.WRITE_EXTERNAL_STORAGE,
      Manifest.permission.READ_EXTERNAL_STORAGE, };

  boolean pickOrChoose = true;
  Button takePhotoButton;
  Button choosePhotoButton;
  Button retryIDButton;
  Button videoScanButton;
  ImageView photoShow;
  TextView photoTags;
  Bitmap chosenBitmap;
  String mTakenPhotoPath;
  String mChoosenPhotoPath;
  String tags;
  String firstTag;
  ClarifaiClient clarifai;
  String AlchemyAPI_Key = Constants.API_KEY;
  List<RecognitionResult> results;
  byte[] photoBytes;
  int limit = 50;
  int newNumCalls;
  String month_name;
  private Toolbar toolbar;
  byte[] videoBytes;
  RelativeLayout rl;

  private GoogleApiClient client;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    toolbar = (Toolbar) findViewById(R.id.my_toolbar);
    setSupportActionBar(toolbar);
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
      getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
      getWindow().setStatusBarColor(getResources().getColor(R.color.colorPrimaryDark));
    }
    getSupportActionBar().setTitle("Photo Tagger");
    takePhotoButton = (Button) findViewById(R.id.takePhotoButton);
    choosePhotoButton = (Button) findViewById(R.id.choosePhotoButton);
    retryIDButton = (Button) findViewById(R.id.retryIDButton);
    videoScanButton = (Button) findViewById(R.id.videoScanButton);

    photoShow = (ImageView) findViewById(R.id.photoShow);
    photoTags = (TextView) findViewById(R.id.photoTags);
    rl = (RelativeLayout) findViewById(R.id.mainPage);

    getBackground();
    photoTags.setMovementMethod(ScrollingMovementMethod.getInstance());

    retryIDButton.setVisibility(View.GONE);

    clarifai = new ClarifaiClient(Constants.APP_ID, Constants.APP_SECRET);
    buttonListeners();

    client = new GoogleApiClient.Builder(this).addApi(AppIndex.API).build();

    if (!isNetworkAvailable()) {
      createNetworkErrorDialog();
    }

    if (checkPermissions()) {
    } else {
      permissionFailDialogCreate();
    }
  }

  /** * testing13 testing13 testing1323 */
  private void permissionFailDialogCreate() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder
        .setMessage("You need to allow all permissions for the app to interact with photos and videos on your device.")
        .setTitle("Unable to access files").setCancelable(false)
        .setPositiveButton("Enable", new DialogInterface.OnClickListener() {
          public void onClick(DialogInterface dialog, int id) {
            if (checkPermissions()) {

            } else {
              dialog.cancel();
              permissionFailDialogCreate();
            }
          }
        }).setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
          public void onClick(DialogInterface dialog, int id) {
            dialog.cancel();
          }
        });
    AlertDialog alert = builder.create();
    alert.show();
  }

  private boolean checkPermissions() {
    int result;
    List<String> listPermissionsNeeded = new ArrayList<>();
    for (String p : permissions) {
      result = ContextCompat.checkSelfPermission(MainActivity.this, p);
      if (result != PackageManager.PERMISSION_GRANTED) {
        listPermissionsNeeded.add(p);
      }
    }
    if (!listPermissionsNeeded.isEmpty()) {
      ActivityCompat.requestPermissions(this, listPermissionsNeeded.toArray(new String[listPermissionsNeeded.size()]),
          MULT_PERMISSIONS);
      return false;
    }
    return true;
  }

  @Override
  public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
    switch (requestCode) {
      case MULT_PERMISSIONS: {
        if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
        } else {
          permissionFailDialogCreate();
        }
        return;
      }
    }
  }

  @Override
  public boolean onCreateOptionsMenu(Menu menu) {
    getMenuInflater().inflate(R.menu.menu, menu);
    return true;
  }

  @Override
  public boolean onOptionsItemSelected(MenuItem item) {
    int id = item.getItemId();

    if (id == R.id.menu_item_share) {

      if (photoShow.getDrawable() != null) {
        Bitmap b = ((BitmapDrawable) photoShow.getDrawable()).getBitmap();
        Intent share = new Intent(Intent.ACTION_SEND);
        share.setType("image/jpeg");
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        b.compress(Bitmap.CompressFormat.JPEG, 100, bytes);
        String path = MediaStore.Images.Media.insertImage(getContentResolver(), b, "Title", null);
        Uri imageUri = Uri.parse(path);
        share.putExtra(Intent.EXTRA_STREAM, imageUri);
        share.putExtra(Intent.EXTRA_TEXT, "I found these things in this photo: " + tags);
        startActivity(Intent.createChooser(share, "Select"));
        return true;
      } else {
        Toast.makeText(getApplicationContext(), "Please scan a photo first.", Toast.LENGTH_SHORT).show();
      }
    } else if (id == R.id.menu_item_search) {
      onCreateSearchDialog();
    } else if (id == R.id.menu_item_settings) {
      startActivity(new Intent(getApplicationContext(), SettingsActivity.class));
    }

    return super.onOptionsItemSelected(item);
  }

  private void buttonListeners() {
    takePhotoButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {

        if (checkPermissions()) {
        } else {
          permissionFailDialogCreate();
        }
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);

        startActivityForResult(intent, TAKE_PICTURE);
      }
    });
    choosePhotoButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {

        if (checkPermissions()) {
        } else {
          permissionFailDialogCreate();
        }
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType("image/*");
        startActivityForResult(intent, PICK_PHOTO);
      }
    });
    retryIDButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {

        if (checkPermissions()) {
        } else {
          permissionFailDialogCreate();
        }
        if (!reachedMonthlyClarifaiLimit()) {
          updateClarifaiLimit();
          photoTags.setText("Analyzing photo...");
          Bitmap bitmap = ((BitmapDrawable) photoShow.getDrawable()).getBitmap();
          ByteArrayOutputStream stream = new ByteArrayOutputStream();
          bitmap.compress(Bitmap.CompressFormat.PNG, 90, stream);
          photoBytes = stream.toByteArray();
          new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(final Void... params) {
              results = clarifai.recognize(new RecognitionRequest(photoBytes));
              return null;
            }

            @Override
            protected void onPostExecute(final Void result) {
              clarifaiUIUpdate();
            }
          }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR, null);
        } else {
          Toast.makeText(getApplicationContext(),
              "Sorry, advanced scan monthly limit has been reached (" + limit + "/" + limit + ").", Toast.LENGTH_SHORT)
              .show();
        }
      }
    });
    videoScanButton.setOnClickListener(new View.OnClickListener() {
      @Override
      public void onClick(View v) {

        if (checkPermissions()) {
        } else {
          permissionFailDialogCreate();
        }
        pickOrChoose = false;
        Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
        intent.setType("video/*");
        startActivityForResult(intent, PICK_VIDEO);
      }
    });
  }

  private boolean reachedMonthlyClarifaiLimit() {
    boolean reachedLimit = false;

    Calendar now = Calendar.getInstance();
    int currentMonth = now.get(Calendar.MONTH) + 1;
    SharedPreferences sp = getSharedPreferences("user_prefs", Activity.MODE_PRIVATE);
    int retrievedMonth = sp.getInt("currentMonth", -1);
    if (retrievedMonth != currentMonth) {
      SharedPreferences sp2 = getSharedPreferences("user_prefs", Activity.MODE_PRIVATE);
      SharedPreferences.Editor editor = sp2.edit();
      editor.putInt("currentMonth", currentMonth);
      editor.commit();
      retrievedMonth = currentMonth;
    }

    SharedPreferences sp2 = getSharedPreferences("user_prefs", Activity.MODE_PRIVATE);
    int userClarifaiCalls = sp2.getInt("numAPICalls", 0);
    if (userClarifaiCalls == limit && retrievedMonth == currentMonth) {
      reachedLimit = true;
    }

    return reachedLimit;
  }

  private void updateClarifaiLimit() {
    SharedPreferences sp = getSharedPreferences("user_prefs", Activity.MODE_PRIVATE);
    int gotUserClarifaiCalls = sp.getInt("numAPICalls", 0);
    newNumCalls = ++gotUserClarifaiCalls;
    SharedPreferences sp2 = getSharedPreferences("user_prefs", Activity.MODE_PRIVATE);
    SharedPreferences.Editor editor = sp2.edit();

    editor.putInt("numAPICalls", newNumCalls);
    editor.commit();
  }

  private boolean isNetworkAvailable() {
    ConnectivityManager connectivityManager = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
    NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
    return activeNetworkInfo != null && activeNetworkInfo.isConnected();
  }

  protected void createNetworkErrorDialog() {

    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setMessage(
        "You need a network connection to use this application. Please turn on mobile network or Wi-Fi in Settings.")
        .setTitle("Unable to connect").setCancelable(false)
        .setPositiveButton("Settings", new DialogInterface.OnClickListener() {
          public void onClick(DialogInterface dialog, int id) {
            Intent i = new Intent(Settings.ACTION_WIRELESS_SETTINGS);
            startActivity(i);
          }
        }).setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
          public void onClick(DialogInterface dialog, int id) {
            MainActivity.this.finish();
          }
        });
    AlertDialog alert = builder.create();
    alert.show();
  }

  public void onCreateSearchDialog() {
    AlertDialog.Builder builder = new AlertDialog.Builder(this);
    builder.setTitle("Research Tags");

    final EditText input = new EditText(this);
    input.setInputType(InputType.TYPE_CLASS_TEXT);
    if (firstTag == null) {
      input.setHint("try: car");
    } else {
      input.setHint("try: " + firstTag);
    }
    builder.setView(input);

    builder.setPositiveButton("Search", new DialogInterface.OnClickListener() {
      @Override
      public void onClick(DialogInterface dialog, int which) {
        String searchText = input.getText().toString();
        Log.i("user web search: ", searchText);
        if (!searchText.equals("") && !searchText.equals(" ") && searchText != null) {
          Intent intent = new Intent(Intent.ACTION_WEB_SEARCH);
          intent.putExtra(SearchManager.QUERY, searchText);
          startActivity(intent);
        }
      }
    });
    builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
      @Override
      public void onClick(DialogInterface dialog, int which) {
        dialog.cancel();
      }
    });

    builder.show();
  }

  private void clarifaiUIUpdate() {

    Calendar cal = Calendar.getInstance();
    SimpleDateFormat month_date = new SimpleDateFormat("MMMM");
    month_name = month_date.format(cal.getTime());
    Toast.makeText(getApplicationContext(),
        "Remaining advanced scans for " + month_name + ": " + (limit - newNumCalls) + "/" + limit, Toast.LENGTH_LONG)
        .show();

    if (results.get(0).getTags() != null) {

      List<Tag> tagsFound = results.get(0).getTags();
      String tag = "";
      for (int i = 0; i < tagsFound.size(); i++) {
        tag = tagsFound.get(i).getName();
        if (i == 0) {
          firstTag = tag;
          photoTags.setText("Tags: " + tag);
          tags = tag;
        } else {
          photoTags.append(", " + tag);
          tags = tags + ", " + tag;
        }
      }
      Log.i("New photo tags are", tags);
    } else {
      photoTags.setText("No detailed tags could be found...");
    }
    retryIDButton.setVisibility(View.GONE);
  }

  @SuppressLint("LongLogTag")
  @Override
  protected void onActivityResult(int requestCode, int resultCode, Intent intent) {
    if (requestCode == PICK_PHOTO && resultCode == RESULT_OK && intent != null) {
      photoTags.setText("Analyzing photo...");

      Uri selectedImage = intent.getData();
      InputStream inputStream = null;
      mChoosenPhotoPath = selectedImage.getPath();
      if (ContentResolver.SCHEME_CONTENT.equals(selectedImage.getScheme())) {
        try {
          inputStream = this.getContentResolver().openInputStream(selectedImage);
        } catch (FileNotFoundException e) {
          e.printStackTrace();
        }
      } else {
        if (ContentResolver.SCHEME_FILE.equals(selectedImage.getScheme())) {
          try {
            inputStream = new FileInputStream(selectedImage.getPath());
          } catch (FileNotFoundException e) {
            e.printStackTrace();
          }
        }
      }
      chosenBitmap = BitmapFactory.decodeStream(inputStream);

      int currentBitmapWidth = chosenBitmap.getWidth();
      int currentBitmapHeight = chosenBitmap.getHeight();

      int ivWidth = photoShow.getWidth();
      int ivHeight = photoShow.getHeight();
      int newWidth = ivWidth;

      int newHeight = (int) Math
          .floor((double) currentBitmapHeight * ((double) newWidth / (double) currentBitmapWidth));

      Bitmap newbitMap = Bitmap.createScaledBitmap(chosenBitmap, newWidth, newHeight, true);

      photoShow.setImageBitmap(newbitMap);

      SendAlchemyCall("imageClassify");
    }

    else if (requestCode == TAKE_PICTURE && resultCode == RESULT_OK && intent != null) {
      photoTags.setText("Analyzing photo...");
      Bundle extras = intent.getExtras();
      Bitmap bitmap = (Bitmap) extras.get("data");
      ByteArrayOutputStream bos = new ByteArrayOutputStream();
      bitmap.compress(Bitmap.CompressFormat.JPEG, 100, bos);
      byte[] bitmapdata = bos.toByteArray();
      File file = null;
      try {
        file = createImageFile();
      } catch (IOException e) {
        e.printStackTrace();
      }
      FileOutputStream fos = null;
      try {
        fos = new FileOutputStream(file);
      } catch (FileNotFoundException e) {
        e.printStackTrace();
      }
      try {
        fos.write(bitmapdata);
      } catch (IOException e) {
        e.printStackTrace();
      }
      try {
        fos.flush();
      } catch (IOException e) {
        e.printStackTrace();
      }
      try {
        fos.close();
        galleryAddPic();
      } catch (IOException e) {
        e.printStackTrace();
      }
      photoShow.setImageBitmap(BitmapFactory.decodeFile(String.valueOf(new File(mTakenPhotoPath))));
      SendAlchemyCall("imageClassify");

    } else if (requestCode == PICK_VIDEO && resultCode == RESULT_OK && intent != null) {

      if (!reachedMonthlyClarifaiLimit()) {
        updateClarifaiLimit();

        Uri uri = intent.getData();
        if (uri != null) {
        }
        File file = new File(getPath(getApplicationContext(), uri));
        int size = (int) file.length();
        if (size < 34603008) {
          byte[] bytes = new byte[size];
          try {
            BufferedInputStream buf = new BufferedInputStream(new FileInputStream(file));
            buf.read(bytes, 0, bytes.length);
            buf.close();
          } catch (FileNotFoundException e) {
            e.printStackTrace();
          } catch (IOException e) {
            e.printStackTrace();
          }
          videoBytes = bytes;
          if (videoBytes.length != 0 && videoBytes != null) {
            photoTags.setText("Analyzing video...");
            Log.i("videoBytes isn't empty hopefully", (videoBytes.length != 0) + "");
            Bitmap videoThumbnail = ThumbnailUtils.createVideoThumbnail(getPath(getApplicationContext(), uri),
                MediaStore.Video.Thumbnails.FULL_SCREEN_KIND);
            photoShow.setImageBitmap(videoThumbnail);
            Log.i("video is small enough", size + " bytes");
          }

          new AsyncTask<Void, Void, Void>() {
            @Override
            protected Void doInBackground(final Void... params) {
              results = clarifai.recognize(new RecognitionRequest(videoBytes));
              return null;
            }

            @Override
            protected void onPostExecute(final Void result) {
              clarifaiUIUpdate();
            }
          }.executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR, null);
        } else {
          Toast.makeText(getApplicationContext(), "Sorry, video is too big (33MB or bigger).", Toast.LENGTH_SHORT)
              .show();
          Log.i("video is too big (33MB or bigger)", size + " bytes");
        }
      } else {
        Toast.makeText(getApplicationContext(),
            "Sorry, advanced/video scan monthly limit has been reached (" + limit + "/" + limit + ").",
            Toast.LENGTH_SHORT).show();
      }

    }
  }

  private void SendAlchemyCall(final String call) {
    Thread thread = new Thread(new Runnable() {
      @Override
      public void run() {
        try {
          SendAlchemyCallInBackground(call);
        } catch (Exception e) {
          e.printStackTrace();
        }
      }
    });

    thread.start();
  }

  private void SendAlchemyCallInBackground(final String call) {
    Document doc = null;
    AlchemyAPI api = null;
    try {
      api = AlchemyAPI.GetInstanceFromString(AlchemyAPI_Key);
    } catch (IllegalArgumentException ex) {
      return;
    }

    try {
      if ("imageClassify".equals(call)) {
        Bitmap bitmap = ((BitmapDrawable) photoShow.getDrawable()).getBitmap();
        ByteArrayOutputStream stream = new ByteArrayOutputStream();
        bitmap.compress(Bitmap.CompressFormat.JPEG, 100, stream);
        byte[] imageByteArray = stream.toByteArray();

        AlchemyAPI_ImageParams imageParams = new AlchemyAPI_ImageParams();
        imageParams.setImage(imageByteArray);
        imageParams.setImagePostMode(AlchemyAPI_ImageParams.RAW);
        doc = api.ImageGetRankedImageKeywords(imageParams);
        ShowTagInTextView(doc, "text");
      }
    } catch (Exception e) {
      e.printStackTrace();
    }
  }

  private void ShowTagInTextView(final Document doc, final String tag) {
    Log.d(getString(R.string.app_name), doc.toString());
    runOnUiThread(new Runnable() {
      @Override
      public void run() {
        Element root = doc.getDocumentElement();
        NodeList items = root.getElementsByTagName(tag);
        for (int i = 0; i < items.getLength(); i++) {
          Node concept = items.item(i);
          String aString = concept.getChildNodes().item(0).getNodeValue();
          if (i == 0 && aString.equals("NO_TAGS")) {
            photoTags.setText("No simple tags could be found...");
            break;
          } else if (i == 0 && !aString.equals("NO_TAGS")) {
            firstTag = aString;
            photoTags.setText("Tags: " + aString);
            tags = aString;
          } else {
            photoTags.append(", " + aString);
            tags = tags + ", " + aString;
          }
        }
        retryIDButton.setVisibility(View.VISIBLE);

        Log.i("photo tags are", tags);
      }
    });
  }

  private File createImageFile() throws IOException {
    String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
    String imageFileName = "JPEG_" + timeStamp + "_";
    String folder_main = "Photo Tagger";
    File storageDir = new File(Environment.getExternalStorageDirectory(), folder_main);
    if (!storageDir.exists()) {
      storageDir.mkdirs();
    }
    File image = File.createTempFile(imageFileName, ".jpg", storageDir);

    mTakenPhotoPath = image.getAbsolutePath();
    Log.e("Success, file path", mTakenPhotoPath);
    return image;
  }

  private void galleryAddPic() {
    Intent mediaScanIntent = new Intent(Intent.ACTION_MEDIA_SCANNER_SCAN_FILE);
    File f = new File(mTakenPhotoPath);
    Uri contentUri = Uri.fromFile(f);
    mediaScanIntent.setData(contentUri);
    this.sendBroadcast(mediaScanIntent);
    Log.i("added pic to gallery", "yes");
  }

  public void getBackground() {
    SharedPreferences sharedPreference = PreferenceManager.getDefaultSharedPreferences(getBaseContext());
    String codeGot = sharedPreference.getString("background", "tiles");
    switch (codeGot) {
      case "tiles":
        rl.setBackgroundResource(R.drawable.tiles);
        break;
      case "wood":
        rl.setBackgroundResource(R.drawable.darkwood);
        break;
      case "linen":
        rl.setBackgroundResource(R.drawable.blacklinen);
        break;
      default:
        Toast.makeText(getApplicationContext(), "Error: could not set background", Toast.LENGTH_SHORT).show();
    }
  }

  @Override
  public void onStart() {
    super.onStart();
    client.connect();
    Action viewAction = Action.newAction(Action.TYPE_VIEW, Uri.parse("http://host/path"),
        Uri.parse("android-app://com.x10host.dhanushpatel.phototagger/http/host/path"));
    AppIndex.AppIndexApi.start(client, viewAction);
  }

  @Override
  public void onStop() {
    super.onStop();

    Action viewAction = Action.newAction(Action.TYPE_VIEW, "Main Page", Uri.parse("http://host/path"),
        Uri.parse("android-app://com.x10host.dhanushpatel.phototagger/http/host/path"));
    AppIndex.AppIndexApi.end(client, viewAction);
    client.disconnect();
  }

  public static String getPath(final Context context, final Uri uri) {

    final boolean isKitKat = Build.VERSION.SDK_INT >= Build.VERSION_CODES.KITKAT;

    if (isKitKat && DocumentsContract.isDocumentUri(context, uri)) {
      if (isExternalStorageDocument(uri)) {
        final String docId = DocumentsContract.getDocumentId(uri);
        final String[] split = docId.split(":");
        final String type = split[0];

        if ("primary".equalsIgnoreCase(type)) {
          return Environment.getExternalStorageDirectory() + "/" + split[1];
        }
      } else if (isDownloadsDocument(uri)) {

        final String id = DocumentsContract.getDocumentId(uri);
        final Uri contentUri = ContentUris.withAppendedId(Uri.parse("content://downloads/public_downloads"),
            Long.valueOf(id));

        return getDataColumn(context, contentUri, null, null);
      } else if (isMediaDocument(uri)) {
        final String docId = DocumentsContract.getDocumentId(uri);
        final String[] split = docId.split(":");
        final String type = split[0];

        Uri contentUri = null;
        if ("image".equals(type)) {
          contentUri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI;
        } else if ("video".equals(type)) {
          contentUri = MediaStore.Video.Media.EXTERNAL_CONTENT_URI;
        } else if ("audio".equals(type)) {
          contentUri = MediaStore.Audio.Media.EXTERNAL_CONTENT_URI;
        }

        final String selection = "_id=?";
        final String[] selectionArgs = new String[] { split[1] };

        return getDataColumn(context, contentUri, selection, selectionArgs);
      }
    } else if ("content".equalsIgnoreCase(uri.getScheme())) {
      return getDataColumn(context, uri, null, null);
    } else if ("file".equalsIgnoreCase(uri.getScheme())) {
      return uri.getPath();
    }

    return null;
  }

  public static String getDataColumn(Context context, Uri uri, String selection, String[] selectionArgs) {

    Cursor cursor = null;
    final String column = "_data";
    final String[] projection = { column };

    try {
      cursor = context.getContentResolver().query(uri, projection, selection, selectionArgs, null);
      if (cursor != null && cursor.moveToFirst()) {
        final int column_index = cursor.getColumnIndexOrThrow(column);
        return cursor.getString(column_index);
      }
    } finally {
      if (cursor != null)
        cursor.close();
    }
    return null;
  }

  public static boolean isExternalStorageDocument(Uri uri) {
    return "com.android.externalstorage.documents".equals(uri.getAuthority());
  }

  public static boolean isDownloadsDocument(Uri uri) {
    return "com.android.providers.downloads.documents".equals(uri.getAuthority());
  }

  public static boolean isMediaDocument(Uri uri) {
    return "com.android.providers.media.documents".equals(uri.getAuthority());
  }

}