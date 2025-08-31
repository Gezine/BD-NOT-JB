package org.bdj;

import java.io.*;
import java.net.*;
import java.lang.reflect.Method;
import java.util.jar.JarFile;
import java.util.jar.Manifest;
import java.util.jar.Attributes;
import org.dvb.lang.DVBClassLoader;

public class RemoteJarLoader implements Runnable {
    
    public void run() {
        try {
            ServerSocket server = new ServerSocket(9025);
            Status.println("JAR Loader listening on port 9025...");
            
            while (true) {
                Socket client = server.accept();
                try {
                    loadAndRunJar(client);
                } catch (Exception e) {
                    Status.printStackTrace("Error processing JAR", e);
                }
                
                client.close();
                Status.println("Waiting for next JAR on port 9025...");
            }
        } catch (IOException e) {
            Status.printStackTrace("Server error", e);
        }
    }
    
    private static void loadAndRunJar(Socket client) throws Exception {
        String jarPath = "/OS/HDD/download0/mnt_ada/received.jar";
        
        InputStream inputStream = client.getInputStream();
        
        OutputStream outputStream = new FileOutputStream(jarPath);
        
        byte[] buf = new byte[8192];
        int total = 0;
        int read;
        
        Status.println("Receiving JAR...");
        while ((read = inputStream.read(buf)) > 0) {
            outputStream.write(buf, 0, read);
            total += read;
        }
        
        outputStream.close();
        inputStream.close();
        Status.println("JAR received: " + total + " bytes total");
        
        runJar(new File(jarPath));
    }
    
    private static void runJar(File jarFile) throws Exception {
        JarFile jar = new JarFile(jarFile);
        Manifest manifest = jar.getManifest();
        jar.close();
        
        if (manifest == null) {
            throw new Exception("No manifest found in JAR");
        }
        
        String mainClassName = manifest.getMainAttributes().getValue(Attributes.Name.MAIN_CLASS);
        if (mainClassName == null) {
            throw new Exception("No Main-Class specified in manifest");
        }
        
        ClassLoader currentLoader = RemoteJarLoader.class.getClassLoader();
        
        // Create DVBClassLoader with the JAR URL and XletClassLoader as parent
        URL jarUrl = jarFile.toURL();
        URL[] urls = new URL[]{jarUrl};
        
        DVBClassLoader dvbLoader = DVBClassLoader.newInstance(urls, currentLoader);
        
        Class mainClass = dvbLoader.loadClass(mainClassName);
        
        Method mainMethod = mainClass.getMethod("main", new Class[]{String[].class});

        Status.println("Running " + mainClassName + "...");
        
        mainMethod.invoke(null, new Object[]{new String[0]});
        Status.println(mainClassName + " execution completed");
        
    }
}