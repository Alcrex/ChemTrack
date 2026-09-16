using System;
using System.Diagnostics;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows;

namespace ChemTrack.Desktop;

public partial class MainWindow : Window
{
    private Process? _backendProcess;

    private readonly HttpClient _httpClient = new()
    {
        Timeout = TimeSpan.FromSeconds(2)
    };

    public MainWindow()
    {
        InitializeComponent();
        Loaded += MainWindow_Loaded;
    }

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        try
        {
            await StartBackendAsync();

            await Browser.EnsureCoreWebView2Async();

            Browser.CoreWebView2.Navigate(
                "http://localhost:8080/"
            );
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                $"启动 ChemTrack 失败：{ex.Message}",
                "启动错误",
                MessageBoxButton.OK,
                MessageBoxImage.Error
            );
        }
    }

    private async Task StartBackendAsync()
    {
        if (await IsBackendReadyAsync())
        {
            return;
        }

        string jarPath = Path.Combine(
            AppContext.BaseDirectory,
            "backend",
            "chemtrack-backend.jar"
        );

        if (!File.Exists(jarPath))
        {
            throw new FileNotFoundException(
                "找不到后端 JAR 文件",
                jarPath
            );
        }

        string? workingDirectory = Path.GetDirectoryName(jarPath);

        var startInfo = new ProcessStartInfo
        {
            FileName = "java.exe",
            WorkingDirectory = workingDirectory,
            UseShellExecute = false,
            CreateNoWindow = true
        };

        startInfo.ArgumentList.Add("-jar");
        startInfo.ArgumentList.Add(jarPath);

        _backendProcess = Process.Start(startInfo);

        if (_backendProcess == null)
        {
            throw new Exception("无法启动后端 JAR 文件。");
        }

        for (int i = 0; i < 30; i++)
        {
            if (await IsBackendReadyAsync())
            {
                return;
            }

            await Task.Delay(500);
        }

        throw new Exception(
            "后端启动超时，请检查 Java、MySQL 和数据库密码配置。"
        );
    }

    private async Task<bool> IsBackendReadyAsync()
    {
        try
        {
            using HttpResponseMessage response =
                await _httpClient.GetAsync(
                    "http://localhost:8080/api/health"
                );

            return response.IsSuccessStatusCode;
        }
        catch
        {
            return false;
        }
    }

    protected override void OnClosed(EventArgs e)
    {
        if (_backendProcess is { HasExited: false })
        {
            _backendProcess.Kill(entireProcessTree: true);
        }

        _httpClient.Dispose();

        base.OnClosed(e);
    }
}