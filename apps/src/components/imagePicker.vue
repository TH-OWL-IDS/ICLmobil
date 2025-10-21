/*
 * Copyright 2025 Sascha Martinetz - Fraunhofer IOSB-INA
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
<script>
import { f7 } from 'framework7-vue';
import userService from '../services/userService';
import { createThumbnail } from '../js/utilities/imageUtils';

export default {
    data() {
        return {
            camera: this.$store.getters.getPluginCamera,
            file: this.$store.getters.getPluginFile,
            fileTransfer: this.$store.getters.getPluginFileTransfer,
            fileUploadOptions: this.$store.getters.getPluginFileUploadOptions,
            targetPath: "/ImageUploads/",
            imageProofTemp: null,
            imageProofTempBase64: null,
            fullImageBase64: null,
            fullImageProofBase64: null
        }
    },
    computed: {
        imageTemp: {
            get() {
                return this.$store.getters.getUserImageTempUrl + '?t=' + this.$store.getters.getUserUpdatedImageAt;
            },
            set(v) {
                this.$store.dispatch('setUserImageTempUrl', { imageURL: v });
            }
        },
        imageTempBase64: {
            get() {
                return this.$store.getters.getUserImageTempBase64;
            },
            set(v) {
                this.$store.dispatch('setUserImageTempBase64', { imageBase64: v });
            }
        }
    },
    methods: {
        takeImage(isRegistered) {
            try {
                if (this.camera == null)
                    return;

                console.log("Getting image from camera...");
                var options = 
                { 
                    quality: 60, 
                    destinationType: this.camera.DestinationType.FILE_URI,
                    correctOrientation: true
                };

                this.camera.getPicture(
                    (imageUri) => {
                        // Set image URL as temporary image for iOS
                        if (f7.device.ios) {
                            this.imageTemp = window.WkWebView.convertFilePath(imageUri);
                        }
                        // Get temporary image and convert to temporary base64 string
                        window.resolveLocalFileSystemURL(imageUri, (fileEntry) => {
                            fileEntry.file((file) => {
                                var reader = new FileReader();
                                reader.onloadend = async () => {
                                    var dataUrl = reader.result;
                                    var base64String = dataUrl.split(',')[1];

                                    // Generate thumbnail
                                    const thumbnailDataUrl = await createThumbnail(dataUrl, 256, 256);
                                    const thumbnailBase64 = thumbnailDataUrl.split(',')[1];

                                    this.imageTempBase64 = thumbnailBase64;
                                    this.fullImageBase64 = base64String;
                                    
                                    // Set dataUrl URL as temporary image for Android
                                    if (f7.device.android) {
                                        this.imageTemp = dataUrl;
                                    }
                                    // Is user registered? Then upload the base64 image data...
                                    if (isRegistered) {
                                        this.uploadUserImage();
                                    }
                                };
                                reader.readAsDataURL(file);
                            });
                        });
                    }, (error) => {
                        f7.dialog.alert(this.$t('app.dialog.error.taking-image-failed') + error, this.$t('app.dialog.error.title'));
                    }, options);
            } catch(err) {
                console.log(err);
            }
        },
        async getImage(isRegistered) {
            try {
                if (this.camera == null)
                    return;
                
                const isIPad = (f7.device.ios && f7.device.ipad);

                if (isIPad) {
                    console.log("IPAD erkannt. Verwende nativen HTML File Picker als Workaround.");
                    await this.getBase64FromNativeFile(isRegistered);
                } else {
                    var srcType = this.camera.PictureSourceType.SAVEDPHOTOALBUM;
                    var options = this.setOptions(srcType);

                    return new Promise((resolve, reject) => {
                        this.camera.getPicture(
                            (imageUri) => {
                                if (f7.device.ios) {
                                    this.imageTemp = window.WkWebView.convertFilePath(imageUri);
                                }
                                window.resolveLocalFileSystemURL(imageUri, (fileEntry) => {
                                    fileEntry.file(async (file) => {
                                        var reader = new FileReader();
                                        reader.onloadend = async () => {
                                            const dataUrl = reader.result;
                                            await this.processImage(dataUrl, isRegistered);
                                            resolve();
                                        };
                                        reader.readAsDataURL(file);
                                    });
                                });
                            }, (error) => {
                                f7.dialog.alert(this.$t('app.dialog.error.getting-image-failed') + error, this.$t('app.dialog.error.title'));
                                reject(error);
                            }, options);
                    });
                }
            } catch(err) {
                console.error("Fehler in getImage:", err);
                if (err !== 'Auswahl abgebrochen oder leer.') {
                    f7.dialog.alert(this.$t('app.dialog.error.getting-image-failed') + err, this.$t('app.dialog.error.title'));
                }
            }
        },
        takeImageProof(geoLocation, id) {
            try {
                if (this.camera == null)
                    return;

                console.log("Getting image from camera...");
                var options = 
                { 
                    quality: 80, 
                    destinationType: this.camera.DestinationType.FILE_URI,
                    correctOrientation: true
                };

                this.camera.getPicture(
                    (imageUri) => {
                        // Set image URL as temporary image for iOS
                        if (f7.device.ios) {
                            this.imageProofTemp = window.WkWebView.convertFilePath(imageUri);
                        }
                        // Get temporary image and convert to temporary base64 string
                        window.resolveLocalFileSystemURL(imageUri, (fileEntry) => {
                            fileEntry.file((file) => {
                                var reader = new FileReader();
                                reader.onloadend = async () => {
                                    var dataUrl = reader.result;
                                    var base64String = dataUrl.split(',')[1];

                                    // Generate thumbnail
                                    const thumbnailDataUrl = await createThumbnail(dataUrl, 1024, 1024);
                                    const thumbnailBase64 = thumbnailDataUrl.split(',')[1];

                                    this.imageProofTempBase64 = thumbnailBase64;
                                    this.fullImageProofBase64 = base64String;

                                    // Set dataUrl URL as temporary image for Android
                                    if (f7.device.android) {
                                        this.imageProofTemp = dataUrl;
                                    }
                                    // Upload the base64 image data...
                                    this.uploadImageProof(geoLocation, id);
                                };
                                reader.readAsDataURL(file);
                            });
                        });
                    }, (error) => {
                        f7.dialog.alert(this.$t('app.dialog.error.taking-image-failed') + error, this.$t('app.dialog.error.title'));
                    }, options);
            } catch(err) {
                console.log(err);
            }
        },
        setOptions(srcType) {
            var options = {
                quality: 50,
                destinationType: this.camera.DestinationType.FILE_URI,
                sourceType: srcType,
                encodingType: this.camera.EncodingType.JPEG,
                mediaType: this.camera.MediaType.PICTURE,
                correctOrientation: true
            }
            return options;
        },
        async uploadUserImage() {
            try {
                console.log("UPLOADING IMAGE...");
                const data = {
                    profileImage: this.imageTempBase64
                };
                const response = await userService.uploadUserImage(data);
                if (response.status === 200) {
                    console.log("UPLOAD SUCCESSFULL!");

                    this.$store.dispatch('setUserImage');
                    this.$store.dispatch('setUserImageUpdatedAt', { updated: new Date().getTime() });

                    this.imageTempBase64 = null;
                    this.imageTemp = null;
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.servertext'), this.$t('app.dialog.error.title'));
                }
            } catch (error) {
                console.log("error: ", error)
            }
        },
        async uploadImageProof(geoLocation, id) {
            try {
                console.log("UPLOADING PROOF IMAGE...");
                const data = {
                    image: this.imageProofTempBase64,
                    latitude: geoLocation.latitude,
                    longitude: geoLocation.longitude,
                    booking_id: id
                };
                console.log("TAKE IMAGE DATA: ", data)
                const response = await userService.uploadImageProof(data);
                if (response.status === 200) {
                    console.log("UPLOAD IMAGE PROOF SUCCESSFULL!");
                    this.imageProofTempBase64 = null;
                    this.imageProofTemp = null;
                } else {
                    f7.dialog.alert(this.$t('app.dialog.error.servertext'), this.$t('app.dialog.error.title'));
                }
            } catch (error) {
                console.log("error: ", error)
            }
        },
        async getBase64FromNativeFile(isRegistered) {
            try {
                const file = await this.choosePhoto(); 
                
                return new Promise((resolve, reject) => {
                    const reader = new FileReader();

                    reader.onloadend = async () => {
                        const dataUrl = reader.result;
                        
                        var base64String = dataUrl.split(',')[1];
                        
                        const thumbnailDataUrl = await createThumbnail(dataUrl, 256, 256);
                        const thumbnailBase64 = thumbnailDataUrl.split(',')[1];

                        this.imageTempBase64 = thumbnailBase64;
                        this.fullImageBase64 = base64String;

                        this.imageTemp = thumbnailDataUrl;
                        
                        if (isRegistered) {
                            await this.uploadUserImage();
                        }
                        resolve();
                    };
                    
                    reader.onerror = reject;
                    reader.readAsDataURL(file); 
                });

            } catch (error) {
                if (error !== 'Auswahl abgebrochen oder leer.') {
                    throw error;
                }
            }
        },
        async processImage(dataUrl, isRegistered) {
            var base64String = dataUrl.split(',')[1];

            // Generate thumbnail
            const thumbnailDataUrl = await createThumbnail(dataUrl, 256, 256);
            const thumbnailBase64 = thumbnailDataUrl.split(',')[1];

            this.imageTempBase64 = thumbnailBase64;
            this.fullImageBase64 = base64String;

            // Set dataUrl URL as temporary image for Android (oder für Native Picker)
            if (f7.device.android || !f7.device.ios) { // Native Picker gibt DataURL, die hier verwendet werden kann
                this.imageTemp = dataUrl;
            }
            
            // Is user registered? Then upload the base64 image data...
            if (isRegistered) {
                await this.uploadUserImage();
            }
        },
        choosePhoto() {
            return new Promise((resolve, reject) => {
                const input = document.createElement('input');
                input.type = 'file';
                input.accept = 'image/*';
                input.style.display = 'none';

                input.onchange = (event) => {
                    const file = event.target.files && event.target.files[0];
                    if (file) {
                        resolve(file);
                    } else {
                        reject('Auswahl abgebrochen oder leer.');
                    }
                    document.body.removeChild(input);
                };
                
                document.body.appendChild(input);
                input.click();
            });
        }
    }
}
</script>

<template>
</template>