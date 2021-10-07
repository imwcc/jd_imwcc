package com.example.ck_upload;

import android.app.ProgressDialog;
import android.content.Context;
import android.os.Bundle;

import com.google.android.material.appbar.CollapsingToolbarLayout;
import com.google.android.material.floatingactionbutton.FloatingActionButton;
import com.google.android.material.snackbar.Snackbar;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.util.Log;
import android.view.View;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.EditText;

import com.example.ck_upload.databinding.ActivityScrollingBinding;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.concurrent.TimeUnit;

import okhttp3.FormBody;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class ScrollingActivity extends AppCompatActivity {
    final String TAG = "imwcc";
    String HOST_ADDRES = "http://s1.s100.vip:22468";
    final Context context = this;

    private Button submit_button;
    private Button ping_button;

    private ActivityScrollingBinding binding;

    final int PING_SERVER_SUCCESS = 1;
    final int PING_SERVER_FAILED = 2;
    final int INPUT_IS_INVALID = 3;
    final int SUBMIT_SUCCESS = 4;
    final int SUBMIT_FAIL = 5;
    final int SHOW_LOADING_DIALOG = 6;
    final int DISMISS_LOADING_DIALOG = 7;

    private EditText pt_pin;
    private EditText wskey;
    private EditText pt_key;
    private EditText push_token;
    private EditText wechart_id;

    private EditText server_address;

    private ProgressDialog progressDialog;

    final Handler handler = new Handler(new Handler.Callback() {
        @Override
        public boolean handleMessage(@NonNull Message msg) {
            switch (msg.what) {
                case PING_SERVER_SUCCESS:
                    Snackbar.make(submit_button, (String)msg.obj, Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    submit_button.setEnabled(true);
                    break;

                case PING_SERVER_FAILED:
                    Snackbar.make(submit_button, (String)msg.obj, Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    submit_button.setEnabled(false);
                    break;

                case INPUT_IS_INVALID:
                    Snackbar.make(submit_button, "Error: " + (String) msg.obj, Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    break;

                case SUBMIT_SUCCESS:
                    Snackbar.make(submit_button, "CK 提交成功", Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    break;

                case SUBMIT_FAIL:
                    Snackbar.make(submit_button, "CK 提交失败: "+(String) msg.obj, Snackbar.LENGTH_LONG)
                            .setAction("Action", null).show();
                    break;

                case SHOW_LOADING_DIALOG:
                    buildProgressDialog("服务器加载中");
                    break;

                case DISMISS_LOADING_DIALOG:
                    cancelProgressDialog();
                    break;
                default:
                    break;
            }
            return true;
        }
    });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityScrollingBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        Toolbar toolbar = binding.toolbar;
        setSupportActionBar(toolbar);
        CollapsingToolbarLayout toolBarLayout = binding.toolbarLayout;
        toolBarLayout.setTitle(getTitle());

        FloatingActionButton fab = binding.fab;
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                submit_button.setEnabled(false);
                ping_server();
            }
        });

        submit_button = findViewById(R.id.submit_ck);
        submit_button.setEnabled(false);
        ping_button = findViewById(R.id.ping_server);
        submit_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                post_ck_info();
            }
        });

        ping_button.setVisibility(View.GONE);


        pt_pin = findViewById(R.id.pt_pin);
        pt_key = findViewById(R.id.pt_key);
        wskey = findViewById(R.id.wskey);
        push_token = findViewById(R.id.pushplus_token);
        wechart_id = findViewById(R.id.wechart_id);
        server_address = findViewById(R.id.server_address);
        progressDialog = new ProgressDialog(this);
        progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);

    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_scrolling, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    @Override
    protected void onResume() {
        super.onResume();
        HOST_ADDRES = server_address.getText().toString();
    }

    /**
     * 同步Get方法
     */
    private void okHttp_synchronousGet() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String url = "https://api.github.com/";
                    OkHttpClient client = new OkHttpClient();
                    Request request = new Request.Builder().url(url).build();
                    okhttp3.Response response = client.newCall(request).execute();
                    if (response.isSuccessful()) {
                        Log.i(TAG, response.body().string());
                    } else {
                        Log.i(TAG, "okHttp is request error");
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }).start();
    }

    private void ping_server() {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String url = HOST_ADDRES + "/ping_server";
                    Log.i(TAG, "url: " + url);
                    OkHttpClient client = new OkHttpClient();
                    Request request = new Request.Builder().url(url).build();
                    okhttp3.Response response = client.newCall(request).execute();
                    Message message = handler.obtainMessage();
                    if (response.isSuccessful()) {
                        Log.i(TAG, "ping success ful");
                        message.obj = "Ping服务器成功";
                        message.what = PING_SERVER_SUCCESS;
                        handler.sendMessage(message);
                    } else {
                        message.what = PING_SERVER_FAILED;
                        message.obj = "Ping服务器失败";
                        handler.sendMessage(message);
                        Log.i(TAG, "okHttp is request error");
                    }
                } catch (IOException e) {
                    Message message = handler.obtainMessage();
                    message.what = PING_SERVER_FAILED;
                    message.obj = "Ping服务器失败";
                    handler.sendMessage(message);
                    e.printStackTrace();
                }
            }
        }).start();
    }

    /**
     * 加载框
     */
    public void buildProgressDialog(String message) {
        if (progressDialog == null) {
            progressDialog = new ProgressDialog(context);
            progressDialog.setProgressStyle(ProgressDialog.STYLE_SPINNER);
        }
        progressDialog.setMessage(message);
        progressDialog.setCancelable(true);
        progressDialog.show();
    }

    /**
     * @Description: TODO 取消加载框
     * @author Sunday
     * @date 2015年12月25日
     */
    public void cancelProgressDialog() {
        if (progressDialog != null)
            if (progressDialog.isShowing()) {
                progressDialog.dismiss();
            }
    }

    private void post_ck_info() {
        if ("".equals(wskey.getText().toString().trim())) {
            Message message = handler.obtainMessage();
            message.what = INPUT_IS_INVALID;
            message.obj = "wskey是空的";
            handler.sendMessage(message);
            return;
        }

        if ("".equals(pt_pin.getText().toString().trim())) {
            Message message = handler.obtainMessage();
            message.what = INPUT_IS_INVALID;
            message.obj = "pt_pin 是空的";
            handler.sendMessage(message);
            return;
        }
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    Message message = handler.obtainMessage();
                    message.what = SHOW_LOADING_DIALOG;
                    handler.sendMessage(message);

                    String url = HOST_ADDRES + "/ck";
                    OkHttpClient okHttpClient = new OkHttpClient();
//                            connectTimeout(10, TimeUnit.SECONDS)
//                            .readTimeout(5, TimeUnit.SECONDS)
//                            .writeTimeout(5, TimeUnit.SECONDS)
//                            .build();
                    JSONObject json = new JSONObject();
                    try {
                        json.put("cookie", "pt_pin=" + pt_pin.getText().toString() + ";pt_key=" + pt_key.getText().toString() + ';');
                        json.put("appkey", "pin="+pt_pin.getText().toString() + ";wskey=" + wskey.getText().toString() + ';');
                        json.put("pushplus_token", push_token.getText().toString());
                        json.put("wechart", wechart_id.getText().toString());
                    } catch (JSONException e) {
                        e.printStackTrace();
                    }

                    RequestBody requestBody = FormBody.create(MediaType.parse("application/json; charset=utf-8")
                            , String.valueOf(json));

                    Request request = new Request.Builder().url(url).post(requestBody).build();
                    Response response = okHttpClient.newCall(request).execute();

                    JSONObject result = new JSONObject(response.body().string());

                    if (response.isSuccessful()) {
                        Log.i(TAG, "ck subimit success ful");
                        Message successsMessage = handler.obtainMessage();
                        successsMessage.what = SUBMIT_SUCCESS;
                        handler.sendMessage(successsMessage);
                    } else {
                        Message successsMessage = handler.obtainMessage();
                        successsMessage.what = SUBMIT_FAIL;
                        successsMessage.obj = result.getString("msg");
                        handler.sendMessage(successsMessage);
                        Log.i(TAG, "ck subimit is request error");
                    }
                } catch (Exception e) {
                    Message message = handler.obtainMessage();
                    message.what = SUBMIT_FAIL;
                    message.obj = "客户端异常";
                    handler.sendMessage(message);
                    e.printStackTrace();
                } finally {
                    Message message = handler.obtainMessage();
                    message.what = DISMISS_LOADING_DIALOG;
                    handler.sendMessage(message);
                }

            }
        }).start();
    }
}