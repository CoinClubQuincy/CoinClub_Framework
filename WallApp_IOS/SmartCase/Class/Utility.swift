//
//  Utility.swift
//  WallApp
//
//  Created by Squareroot on 09/07/18.
//  Copyright © 2018 Squareroot. All rights reserved.
//

import Foundation
import SVProgressHUD
import CoreData
import LocalAuthentication


@objc protocol  UtilityDelegate {
    @objc optional func touchIdLoginResponse(success: Bool, message: String?, error: Error?)
}

class Utility {
    var delegate: UtilityDelegate?
    class func showProgress(_ message: String) {
        SVProgressHUD.setDefaultMaskType(SVProgressHUDMaskType.black)
        if(message == "") {
            SVProgressHUD.show()
        }
        else {
            SVProgressHUD.show(withStatus: message)
        }
    }
    
    class func dismissProgress() {
        SVProgressHUD.dismiss()
    }
    
    class func getContext () -> NSManagedObjectContext {
        let appDelegate = UIApplication.shared.delegate as! AppDelegate
        return appDelegate.persistentContainer.viewContext
    }
    
    static func showAlert(_ title: String, _ message: String, viewController: UIViewController, okButtonTitle: String = "OK", _ isCancelButtonNeeded: Bool = false, cancelButtonTitle: String = "Cancel", okClicked: (() -> Void)? = nil, cancelClicked: (() -> Void)? = nil) {
        let alertController = UIAlertController(title: title, message: message, preferredStyle: UIAlertControllerStyle.alert)
        
        if(isCancelButtonNeeded) {
            let cancelAction = UIAlertAction(title: cancelButtonTitle, style: UIAlertActionStyle.destructive, handler: { (alertAction: UIAlertAction) in
                cancelClicked?()
            })
            alertController.addAction(cancelAction)
        }
        
        let okAction = UIAlertAction(title: okButtonTitle, style: UIAlertActionStyle.destructive, handler: { (alertAction: UIAlertAction) in
            okClicked?()
        })
        
        alertController.addAction(okAction)
        alertController.preferredAction = okAction
        viewController.present(alertController, animated: true, completion: nil)
    }
    
    
    class func showAlertWithTextField(title: String, message: String, viewController: UIViewController, okButtonTitle: String = "OK", isCancelButtonNeeded: Bool = false, cancelButtonTitle: String = "Cancel", textFieldPlaceHolder: String = "", defaultString: String = "", okClicked: ((_ text: String) -> Void)? = nil, cancelClicked: (() -> Void)? = nil) {
        let alertController = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alertController.addTextField { (textField : UITextField!) -> Void in
            textField.placeholder = textFieldPlaceHolder
        }
        alertController.addAction(UIAlertAction(title: okButtonTitle, style: .default, handler: {
            alert -> Void in
            okClicked?((alertController.textFields![0] as UITextField).text!)
        }))
        alertController.addAction(UIAlertAction(title: "Cancel", style: .default, handler: {
            (action : UIAlertAction!) -> Void in
            cancelClicked?()
        }))
        viewController.present(alertController, animated: true, completion: nil)
    }
    
    // MARK: - Touch ID
    func useTouchID(description: String, viewController: UIViewController) {
        let context = LAContext()
        var error: NSError?
        var message : String!
        if context.canEvaluatePolicy(LAPolicy.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            context.evaluatePolicy(LAPolicy.deviceOwnerAuthentication, localizedReason: description) { (success: Bool, error: Error?) in
                if !success {
                    switch (error! as NSError).code {
                    case LAError.systemCancel.rawValue:
                        message = "The system has cancelled the login process";
                    case LAError.userCancel.rawValue:
                        message = "The user has cancelled the login process";
                    case LAError.userFallback.rawValue:
                        message = "The user has chosen alternative method for login";
                    default:
                        if #available(iOS 11.0, *) {
                            switch (error! as NSError).code {
                            case LAError.biometryLockout.rawValue, LAError.appCancel.rawValue:
                                message = error!.localizedDescription
                                message = error!.localizedDescription
                            default:
                                message = error!.localizedDescription
                            }
                        } else {
                            // Fallback on earlier versions
                        }
                        break;
                    }
                }
                
                DispatchQueue.main.async {
                    self.delegate?.touchIdLoginResponse?(success: success, message: message, error: error)
                }
            }
        } else{
            if #available(iOS 11.0, *) {
                switch error!.code {
                case LAError.biometryNotEnrolled.rawValue:
                    message = "User has not configurated the TouchID";
                    break;
                case LAError.passcodeNotSet.rawValue:
                    message = "User has not configurated the password";
                    break;
                case LAError.biometryNotAvailable.rawValue:
                    message = "User has not configurated the password";
                    break;
                case LAError.biometryLockout.rawValue:
                    message = error!.localizedDescription
                case LAError.appCancel.rawValue:
                    message = error!.localizedDescription
                default:
                    message = error!.localizedDescription
                }
            }
            else {
                switch error!.code {
                case LAError.touchIDNotEnrolled.rawValue:
                    message = "User has not configurated the TouchID";
                    break;
                case LAError.passcodeNotSet.rawValue:
                    message = "User has not configurated the password";
                    break;
                case LAError.touchIDNotAvailable.rawValue:
                    message = "User has not configurated the password";
                    break;
                default:
                    switch error!.code {
                    case LAError.touchIDLockout.rawValue:
                        message = error!.localizedDescription
                    case LAError.appCancel.rawValue:
                        message = error!.localizedDescription
                    default:
                        message = error!.localizedDescription
                    }
                }
            }
            DispatchQueue.main.async {
                self.delegate?.touchIdLoginResponse?(success: false, message: message, error: error)
            }
        }
    }
    
    class func savePasscode(passcode: String) {
        UserDefaults.standard.setValue(passcode, forKey: PASSCODE)
        UserDefaults.standard.synchronize()
    }
    
    class func getPasscode() -> String {
        let passcode = UserDefaults.standard.string(forKey: PASSCODE)
        return passcode ?? ""
    }
    
    class func savePasscodeType(passcode: Int) {
        UserDefaults.standard.setValue(passcode, forKey: PASSCODE_TYPE)
        UserDefaults.standard.synchronize()
    }
    
    class func getPasscodeType() -> Int {
        let passcode = UserDefaults.standard.integer(forKey: PASSCODE_TYPE)
        return passcode
    }
}

